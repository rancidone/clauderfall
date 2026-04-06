"""Local MCP adapter registry for the first Clauderfall tool surface."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from clauderfall import debug_log
from clauderfall.mcp.shared import (
    MCPToolSpec,
    MCPValidationError,
    build_services_for_repo_root,
    map_runtime_result,
    optional_bool,
    optional_string,
    require_object,
    require_string_list,
    require_string,
    validation_failure,
)
from clauderfall.runtime import FlushReason, RuntimeServices


ToolHandler = Callable[[RuntimeServices, dict[str, Any]], dict[str, Any]]


@dataclass
class ClauderfallMCPServer:
    """Thin local tool registry over the runtime service surface."""

    repo_root: Path
    docs_root: Path | None = None
    _services: RuntimeServices | None = None
    _handlers: dict[str, tuple[MCPToolSpec, ToolHandler]] = field(default_factory=dict)

    def register_tool(
        self,
        *,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: ToolHandler,
    ) -> None:
        self._handlers[name] = (
            MCPToolSpec(name=name, description=description, input_schema=input_schema),
            handler,
        )

    def list_tools(self) -> list[MCPToolSpec]:
        return [spec for spec, _ in self._handlers.values()]

    def has_tool(self, name: str) -> bool:
        return name in self._handlers

    def call_tool(self, name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if name not in self._handlers:
            debug_log.warning("call_tool: unknown tool %r", name)
            return validation_failure(code="unknown_tool", message=f"unknown tool: {name}")

        _, handler = self._handlers[name]
        debug_log.debug("call_tool: %r payload=%r", name, payload)
        try:
            result = handler(self.services, payload or {})
            debug_log.debug("call_tool: %r result=%r", name, result)
            return result
        except MCPValidationError as exc:
            debug_log.warning("call_tool: %r validation error: %s", name, exc)
            return validation_failure(code="invalid_input", message=str(exc))
        except Exception as exc:
            debug_log.exception("call_tool: %r unhandled exception: %s", name, exc)
            return validation_failure(code="internal_error", message=f"internal error: {exc}")

    @property
    def services(self) -> RuntimeServices:
        if self._services is None:
            self._services = build_services_for_repo_root(
                self.repo_root,
                self.docs_root,
            )
        return self._services


def create_server(repo_root: str | Path, docs_root: str | Path | None = None) -> ClauderfallMCPServer:
    """Build the first flat Clauderfall MCP tool surface."""

    server = ClauderfallMCPServer(
        repo_root=Path(repo_root),
        docs_root=Path(docs_root) if docs_root is not None else None,
    )
    _register_discovery_tools(server)
    _register_design_tools(server)
    _register_session_lifecycle_tools(server)
    return server


def _register_discovery_tools(server: ClauderfallMCPServer) -> None:
    server.register_tool(
        name="discovery_read",
        description="Read the authoritative Discovery artifact. short (default): orientation metadata only. full: adds problem_areas, cross_cutting, and markdown body.",
        input_schema={
            "type": "object",
            "properties": {
                "brief_id": {"type": "string"},
                "checkpoint_id": {"type": "string"},
                "view": {"type": "string", "enum": ["short", "full"]},
            },
            "required": ["brief_id"],
            "additionalProperties": False,
        },
        handler=_discovery_read,
    )
    server.register_tool(
        name="discovery_write",
        description="Persist a Discovery checkpoint without performing a stage transition.",
        input_schema={
            "type": "object",
            "properties": {
                "brief_id": {"type": "string"},
                "markdown": {"type": "string"},
                "sidecar": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "status": {"type": "string", "enum": ["draft", "accepted"]},
                        "readiness": {"type": "string", "enum": ["low", "medium", "high"]},
                        "readiness_rationale": {"type": "string"},
                        "blocking_gaps": {"type": "array", "items": {"type": "string"}},
                        "problem_areas": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "problem_area_id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                                    "source_section": {"type": "string"},
                                    "assumptions": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "assumption_id": {"type": "string"},
                                                "statement": {"type": "string"},
                                                "status": {"type": "string", "enum": ["confirmed", "inferred", "unknown"]},
                                            },
                                            "required": ["assumption_id", "statement", "status"],
                                        },
                                    },
                                },
                                "required": ["problem_area_id", "title", "confidence", "source_section", "assumptions"],
                            },
                        },
                        "cross_cutting": {
                            "type": "object",
                            "properties": {
                                "global_constraints": {"type": "array", "items": {"type": "string"}},
                                "shared_assumptions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "assumption_id": {"type": "string"},
                                            "statement": {"type": "string"},
                                            "status": {"type": "string", "enum": ["confirmed", "inferred", "unknown"]},
                                        },
                                        "required": ["assumption_id", "statement", "status"],
                                    },
                                },
                                "systemic_risks": {"type": "array", "items": {"type": "string"}},
                                "open_questions": {"type": "array", "items": {"type": "string"}},
                                "source_sections": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                    },
                    "required": ["title", "status", "readiness", "readiness_rationale", "blocking_gaps", "problem_areas", "cross_cutting"],
                },
            },
            "required": ["brief_id", "markdown", "sidecar"],
            "additionalProperties": False,
        },
        handler=_discovery_write,
    )
    server.register_tool(
        name="discovery_to_design",
        description="Execute the explicit Discovery-to-Design transition.",
        input_schema={
            "type": "object",
            "properties": {
                "brief_id": {"type": "string"},
                "override": {"type": "boolean"},
            },
            "required": ["brief_id"],
            "additionalProperties": False,
        },
        handler=_discovery_to_design,
    )
    server.register_tool(
        name="discovery_delete",
        description="Delete one Discovery brief and all of its persisted runtime state.",
        input_schema={
            "type": "object",
            "properties": {
                "brief_id": {"type": "string"},
            },
            "required": ["brief_id"],
            "additionalProperties": False,
        },
        handler=_discovery_delete,
    )


def _register_design_tools(server: ClauderfallMCPServer) -> None:
    server.register_tool(
        name="design_read",
        description="Read the authoritative Design unit. short (default): orientation metadata only. full: adds open_questions, assumptions, and markdown body.",
        input_schema={
            "type": "object",
            "properties": {
                "unit_id": {"type": "string"},
                "checkpoint_id": {"type": "string"},
                "view": {"type": "string", "enum": ["short", "full"]},
            },
            "required": ["unit_id"],
            "additionalProperties": False,
        },
        handler=_design_read,
    )
    server.register_tool(
        name="design_list",
        description="List compact Design unit summaries across the current project.",
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        handler=_design_list,
    )
    server.register_tool(
        name="design_write",
        description="Persist a Design checkpoint from either a full replacement or a checkpoint-relative delta update.",
        input_schema={
            "type": "object",
            "properties": {
                "unit_id": {"type": "string"},
                "markdown": {"type": "string"},
                "base_checkpoint_id": {"type": "string"},
                "sidecar": {
                    "type": "object",
                    "description": "Full sidecar replacement. Use when creating a new design unit or replacing the entire metadata record.",
                    "properties": {
                        "design_unit_id": {"type": "string"},
                        "title": {"type": "string"},
                        "status": {"type": "string", "enum": ["draft"]},
                        "scope_summary": {"type": "string"},
                        "readiness": {"type": "string", "enum": ["low", "medium", "high"]},
                        "readiness_rationale": {"type": "string"},
                        "open_questions": {"type": "array", "items": {"type": "string"}},
                        "assumptions": {"type": "array", "items": {"type": "string"}},
                        "depends_on": {"type": "array", "items": {"type": "string"}},
                        "children": {"type": "array", "items": {"type": "string"}},
                        "parent": {"type": ["string", "null"]},
                    },
                    "required": [
                        "design_unit_id", "title", "status", "scope_summary",
                        "readiness", "readiness_rationale", "open_questions", "assumptions",
                    ],
                },
                "sidecar_patch": {
                    "type": "object",
                    "description": "Partial sidecar update for small edits. Prefer this over full sidecar replacement when only a few metadata fields changed.",
                    "properties": {
                        "design_unit_id": {"type": "string"},
                        "title": {"type": "string"},
                        "status": {"type": "string", "enum": ["draft"]},
                        "scope_summary": {"type": "string"},
                        "readiness": {"type": "string", "enum": ["low", "medium", "high"]},
                        "readiness_rationale": {"type": "string"},
                        "open_questions": {"type": "array", "items": {"type": "string"}},
                        "assumptions": {"type": "array", "items": {"type": "string"}},
                        "depends_on": {"type": "array", "items": {"type": "string"}},
                        "children": {"type": "array", "items": {"type": "string"}},
                        "parent": {"type": ["string", "null"]},
                    },
                    "additionalProperties": False,
                },
                "markdown_operations": {
                    "type": "array",
                    "description": "Checkpoint-relative markdown deltas for localized edits. Prefer these over full markdown replacement when only one or a few sections changed.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "op": {
                                "type": "string",
                                "enum": ["replace_section", "append_to_section", "insert_section_after"],
                            },
                            "heading": {"type": "string"},
                            "after_heading": {"type": "string"},
                            "heading_line": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["op"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["unit_id"],
            "additionalProperties": False,
        },
        handler=_design_write,
    )
    server.register_tool(
        name="design_accept",
        description="Accept the current Design unit as the operator-approved design record.",
        input_schema={
            "type": "object",
            "properties": {
                "unit_id": {"type": "string"},
            },
            "required": ["unit_id"],
            "additionalProperties": False,
        },
        handler=_design_accept,
    )
    server.register_tool(
        name="design_delete",
        description="Delete one Design unit and all of its persisted runtime state.",
        input_schema={
            "type": "object",
            "properties": {
                "unit_id": {"type": "string"},
            },
            "required": ["unit_id"],
            "additionalProperties": False,
        },
        handler=_design_delete,
    )


def _register_session_lifecycle_tools(server: ClauderfallMCPServer) -> None:
    server.register_tool(
        name="session_read_startup_view",
        description="Read the startup-oriented recent-session view.",
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        handler=_session_read_startup_view,
    )
    server.register_tool(
        name="session_read_current",
        description="Read the current carry-forward artifact in full detail.",
        input_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        handler=_session_read_current,
    )
    server.register_tool(
        name="session_write_handoff",
        description="Persist the current carry-forward handoff artifact update.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "work_items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
                "thread_markdown": {"type": "string"},
                "flush_reason": {
                    "type": "string",
                    "enum": [reason.value for reason in FlushReason],
                },
            },
            "required": [
                "title",
                "work_items",
                "thread_markdown",
            ],
            "additionalProperties": False,
        },
        handler=_session_write_handoff,
    )
    server.register_tool(
        name="session_archive_current",
        description="Archive the completed current carry-forward record and update startup state.",
        input_schema={
            "type": "object",
            "properties": {
                "closure_summary": {"type": "string"},
                "archived_thread_markdown": {"type": "string"},
            },
            "required": ["closure_summary"],
            "additionalProperties": False,
        },
        handler=_session_archive_current,
    )


def _discovery_read(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    view = payload.get("view", "short")
    if view not in {"short", "full"}:
        raise MCPValidationError("view must be 'short' or 'full'")
    result = map_runtime_result(
        services.discovery.read(
            brief_id=require_string(payload, "brief_id"),
            checkpoint_id=optional_string(payload, "checkpoint_id"),
            view=view,
        )
    )
    if view == "short":
        return _compact_short_read_result(result, artifact_fields=["brief_id", "title", "status", "readiness"])
    return result


def _discovery_write(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return _status_only_result(map_runtime_result(
        services.discovery.write(
            brief_id=require_string(payload, "brief_id"),
            markdown=require_string(payload, "markdown"),
            sidecar=require_object(payload, "sidecar"),
        )
    ))


def _discovery_to_design(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return _status_only_result(map_runtime_result(
        services.discovery.to_design(
            brief_id=require_string(payload, "brief_id"),
            override=optional_bool(payload, "override"),
        )
    ))


def _discovery_delete(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return _status_only_result(map_runtime_result(
        services.discovery.delete(
            brief_id=require_string(payload, "brief_id"),
        )
    ))


def _design_read(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    view = payload.get("view", "short")
    if view not in {"short", "full"}:
        raise MCPValidationError("view must be 'short' or 'full'")
    result = map_runtime_result(
        services.design.read(
            unit_id=require_string(payload, "unit_id"),
            checkpoint_id=optional_string(payload, "checkpoint_id"),
            view=view,
        )
    )
    if view == "short":
        return _compact_short_read_result(result, artifact_fields=["unit_id", "title", "status", "readiness"])
    return result


def _design_list(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    del payload
    return map_runtime_result(services.design.list())


def _design_write(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    sidecar = payload.get("sidecar")
    if sidecar is not None and not isinstance(sidecar, dict):
        if isinstance(sidecar, str):
            raise MCPValidationError(
                "sidecar must be an object when present; got string. Do not JSON-encode sidecar."
            )
        raise MCPValidationError("sidecar must be an object when present")

    sidecar_patch = payload.get("sidecar_patch")
    if sidecar_patch is not None and not isinstance(sidecar_patch, dict):
        if isinstance(sidecar_patch, str):
            raise MCPValidationError(
                "sidecar_patch must be an object when present; got string. Do not JSON-encode sidecar_patch."
            )
        raise MCPValidationError("sidecar_patch must be an object when present")

    markdown = payload.get("markdown")
    if markdown is not None and (not isinstance(markdown, str) or not markdown):
        raise MCPValidationError("markdown must be a non-empty string when present")

    markdown_operations = payload.get("markdown_operations")
    if markdown_operations is not None:
        if not isinstance(markdown_operations, list):
            raise MCPValidationError("markdown_operations must be an array when present")
        if not all(isinstance(operation, dict) for operation in markdown_operations):
            raise MCPValidationError("markdown_operations entries must be objects")

    return _status_only_result(map_runtime_result(
        services.design.write(
            unit_id=require_string(payload, "unit_id"),
            markdown=markdown,
            sidecar=sidecar,
            sidecar_patch=sidecar_patch,
            markdown_operations=markdown_operations,
            base_checkpoint_id=optional_string(payload, "base_checkpoint_id"),
        )
    ))

def _design_accept(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return _status_only_result(map_runtime_result(
        services.design.accept(unit_id=require_string(payload, "unit_id"))
    ))


def _design_delete(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return _status_only_result(map_runtime_result(
        services.design.delete(unit_id=require_string(payload, "unit_id"))
    ))


def _session_read_startup_view(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    del payload
    return _compact_startup_read_result(map_runtime_result(services.session_lifecycle.session_read_startup_view()))


def _session_read_current(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    del payload
    return map_runtime_result(services.session_lifecycle.session_read_current())


def _session_write_handoff(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    flush_reason_value = payload.get("flush_reason")
    flush_reason = FlushReason.CHECKPOINT
    if flush_reason_value is not None:
        try:
            flush_reason = FlushReason(flush_reason_value)
        except ValueError as exc:
            raise MCPValidationError(f"flush_reason must be one of: {', '.join(reason.value for reason in FlushReason)}") from exc

    return _status_only_result(map_runtime_result(
        services.session_lifecycle.session_write_handoff(
            title=require_string(payload, "title"),
            work_items=require_string_list(payload, "work_items"),
            thread_markdown=require_string(payload, "thread_markdown"),
            flush_reason=flush_reason,
        )
    ))


def _session_archive_current(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    archived_thread_markdown = payload.get("archived_thread_markdown")
    if archived_thread_markdown is not None:
        raise MCPValidationError("archived_thread_markdown is not supported by the current runtime service")
    return _status_only_result(map_runtime_result(
        services.session_lifecycle.session_archive_current(
            closure_summary=require_string(payload, "closure_summary"),
        )
    ))


def _status_only_result(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("result") == "success" and not result.get("warnings"):
        return {"result": "success"}
    if result.get("result") == "success":
        return {"result": "success", "warnings": result["warnings"]}
    return result


def _compact_startup_read_result(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("result") != "success":
        return result
    artifacts = result.get("artifacts", {})
    return {
        "result": "success",
        "artifacts": {
            "current": (
                {
                    "title": artifacts["current"]["title"],
                    "work_items": artifacts["current"].get("work_items", []),
                }
                if artifacts.get("current") is not None
                else None
            ),
            "recent_completed": [
                {
                    "history_id": thread["history_id"],
                    "title": thread["title"],
                }
                for thread in artifacts.get("recent_completed", [])
            ],
        },
    }


def _compact_short_read_result(result: dict[str, Any], *, artifact_fields: list[str]) -> dict[str, Any]:
    if result.get("result") != "success":
        return result
    artifacts = result.get("artifacts", {})
    compact_artifacts = {
        field: artifacts[field]
        for field in artifact_fields
        if field in artifacts
    }
    metadata = result.get("metadata", {})
    compact: dict[str, Any] = {
        "result": "success",
        "artifacts": compact_artifacts,
    }
    checkpoint_id = metadata.get("checkpoint_id")
    if checkpoint_id is not None:
        compact["metadata"] = {"checkpoint_id": checkpoint_id}
    warnings = result.get("warnings")
    if warnings:
        compact["warnings"] = warnings
    return compact
