"""Local MCP adapter registry for the first Clauderfall tool surface."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from clauderfall.mcp.shared import (
    MCPToolSpec,
    MCPValidationError,
    build_services_for_repo_root,
    map_runtime_result,
    optional_bool,
    optional_string,
    parse_view,
    require_object,
    require_string,
    validation_failure,
)
from clauderfall.runtime import FlushReason, RuntimeServices


ToolHandler = Callable[[RuntimeServices, dict[str, Any]], dict[str, Any]]


@dataclass
class ClauderfallMCPServer:
    """Thin local tool registry over the runtime service surface."""

    repo_root: Path
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
            return validation_failure(code="unknown_tool", message=f"unknown tool: {name}")

        _, handler = self._handlers[name]
        try:
            return handler(self.services, payload or {})
        except MCPValidationError as exc:
            return validation_failure(code="invalid_input", message=str(exc))

    @property
    def services(self) -> RuntimeServices:
        if self._services is None:
            self._services = build_services_for_repo_root(self.repo_root)
        return self._services


def create_server(repo_root: str | Path) -> ClauderfallMCPServer:
    """Build the first flat Clauderfall MCP tool surface."""

    server = ClauderfallMCPServer(repo_root=Path(repo_root))
    _register_discovery_tools(server)
    _register_design_tools(server)
    _register_session_lifecycle_tools(server)
    return server


def _register_discovery_tools(server: ClauderfallMCPServer) -> None:
    server.register_tool(
        name="discovery_read",
        description="Read the authoritative Discovery artifact in short or full view.",
        input_schema={
            "type": "object",
            "properties": {
                "brief_id": {"type": "string"},
                "view": {"type": "string", "enum": ["short", "full"]},
                "checkpoint_id": {"type": "string"},
            },
            "required": ["brief_id"],
            "additionalProperties": False,
        },
        handler=_discovery_read,
    )
    server.register_tool(
        name="discovery_write_draft",
        description="Persist a Discovery draft checkpoint without performing a stage transition.",
        input_schema={
            "type": "object",
            "properties": {
                "brief_id": {"type": "string"},
                "markdown": {"type": "string"},
                "sidecar": {"type": "object"},
            },
            "required": ["brief_id", "markdown", "sidecar"],
            "additionalProperties": False,
        },
        handler=_discovery_write_draft,
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


def _register_design_tools(server: ClauderfallMCPServer) -> None:
    server.register_tool(
        name="design_read",
        description="Read the authoritative Design unit in short or full view.",
        input_schema={
            "type": "object",
            "properties": {
                "unit_id": {"type": "string"},
                "view": {"type": "string", "enum": ["short", "full"]},
                "checkpoint_id": {"type": "string"},
            },
            "required": ["unit_id"],
            "additionalProperties": False,
        },
        handler=_design_read,
    )
    server.register_tool(
        name="design_write_draft",
        description="Persist a Design draft checkpoint without acceptance.",
        input_schema={
            "type": "object",
            "properties": {
                "unit_id": {"type": "string"},
                "markdown": {"type": "string"},
                "sidecar": {"type": "object"},
            },
            "required": ["unit_id", "markdown", "sidecar"],
            "additionalProperties": False,
        },
        handler=_design_write_draft,
    )
    server.register_tool(
        name="design_to_review",
        description="Move the current Design unit into explicit review state.",
        input_schema={
            "type": "object",
            "properties": {"unit_id": {"type": "string"}},
            "required": ["unit_id"],
            "additionalProperties": False,
        },
        handler=_design_to_review,
    )
    server.register_tool(
        name="design_accept",
        description="Accept the current Design unit as the operator-approved design record.",
        input_schema={
            "type": "object",
            "properties": {
                "unit_id": {"type": "string"},
                "override": {"type": "boolean"},
            },
            "required": ["unit_id"],
            "additionalProperties": False,
        },
        handler=_design_accept,
    )


def _register_session_lifecycle_tools(server: ClauderfallMCPServer) -> None:
    server.register_tool(
        name="read_recent_session_startup_view",
        description="Read the startup-oriented recent-session view.",
        input_schema={
            "type": "object",
            "properties": {"force_rebuild": {"type": "boolean"}},
            "additionalProperties": False,
        },
        handler=_read_recent_session_startup_view,
    )
    server.register_tool(
        name="read_active_thread",
        description="Read one active thread in full detail.",
        input_schema={
            "type": "object",
            "properties": {"thread_id": {"type": "string"}},
            "required": ["thread_id"],
            "additionalProperties": False,
        },
        handler=_read_active_thread,
    )
    server.register_tool(
        name="write_active_thread_handoff",
        description="Persist one active-thread handoff update and refresh the startup projection.",
        input_schema={
            "type": "object",
            "properties": {
                "thread_id": {"type": "string"},
                "title": {"type": "string"},
                "current_intent_summary": {"type": "string"},
                "next_suggested_action": {"type": "string"},
                "thread_markdown": {"type": "string"},
                "flush_reason": {
                    "type": "string",
                    "enum": [reason.value for reason in FlushReason],
                },
            },
            "required": [
                "thread_id",
                "title",
                "current_intent_summary",
                "next_suggested_action",
                "thread_markdown",
            ],
            "additionalProperties": False,
        },
        handler=_write_active_thread_handoff,
    )
    server.register_tool(
        name="rebuild_recent_session_index",
        description="Deterministically rebuild the repo-level recent-session startup index.",
        input_schema={
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "enum": ["startup_validation", "handoff_recovery", "operator_requested"],
                }
            },
            "additionalProperties": False,
        },
        handler=_rebuild_recent_session_index,
    )
    server.register_tool(
        name="archive_completed_thread",
        description="Archive one completed active thread and update startup state.",
        input_schema={
            "type": "object",
            "properties": {
                "thread_id": {"type": "string"},
                "closure_summary": {"type": "string"},
                "archived_thread_markdown": {"type": "string"},
            },
            "required": ["thread_id", "closure_summary"],
            "additionalProperties": False,
        },
        handler=_archive_completed_thread,
    )


def _discovery_read(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.discovery.read(
            brief_id=require_string(payload, "brief_id"),
            view=parse_view(payload.get("view")),
            checkpoint_id=optional_string(payload, "checkpoint_id"),
        )
    )


def _discovery_write_draft(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.discovery.write_draft(
            brief_id=require_string(payload, "brief_id"),
            markdown=require_string(payload, "markdown"),
            sidecar=require_object(payload, "sidecar"),
        )
    )


def _discovery_to_design(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.discovery.to_design(
            brief_id=require_string(payload, "brief_id"),
            override=optional_bool(payload, "override"),
        )
    )


def _design_read(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.design.read(
            unit_id=require_string(payload, "unit_id"),
            view=parse_view(payload.get("view")),
            checkpoint_id=optional_string(payload, "checkpoint_id"),
        )
    )


def _design_write_draft(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.design.write_draft(
            unit_id=require_string(payload, "unit_id"),
            markdown=require_string(payload, "markdown"),
            sidecar=require_object(payload, "sidecar"),
        )
    )


def _design_to_review(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(services.design.to_review(unit_id=require_string(payload, "unit_id")))


def _design_accept(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.design.accept(
            unit_id=require_string(payload, "unit_id"),
            override=optional_bool(payload, "override"),
        )
    )


def _read_recent_session_startup_view(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.session_lifecycle.read_recent_session_startup_view(
            force_rebuild=optional_bool(payload, "force_rebuild"),
        )
    )


def _read_active_thread(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    return map_runtime_result(
        services.session_lifecycle.read_active_thread(thread_id=require_string(payload, "thread_id"))
    )


def _write_active_thread_handoff(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    flush_reason_value = payload.get("flush_reason")
    flush_reason = FlushReason.CHECKPOINT
    if flush_reason_value is not None:
        try:
            flush_reason = FlushReason(flush_reason_value)
        except ValueError as exc:
            raise MCPValidationError(f"flush_reason must be one of: {', '.join(reason.value for reason in FlushReason)}") from exc

    return map_runtime_result(
        services.session_lifecycle.write_active_thread_handoff(
            thread_id=require_string(payload, "thread_id"),
            title=require_string(payload, "title"),
            current_intent_summary=require_string(payload, "current_intent_summary"),
            next_suggested_action=require_string(payload, "next_suggested_action"),
            thread_markdown=require_string(payload, "thread_markdown"),
            flush_reason=flush_reason,
        )
    )


def _rebuild_recent_session_index(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    reason = payload.get("reason", "operator_requested")
    if not isinstance(reason, str) or reason not in {"startup_validation", "handoff_recovery", "operator_requested"}:
        raise MCPValidationError("reason must be 'startup_validation', 'handoff_recovery', or 'operator_requested'")
    return map_runtime_result(services.session_lifecycle.rebuild_recent_session_index(reason=reason))


def _archive_completed_thread(services: RuntimeServices, payload: dict[str, Any]) -> dict[str, Any]:
    archived_thread_markdown = payload.get("archived_thread_markdown")
    if archived_thread_markdown is not None:
        raise MCPValidationError("archived_thread_markdown is not supported by the current runtime service")
    return map_runtime_result(
        services.session_lifecycle.archive_completed_thread(
            thread_id=require_string(payload, "thread_id"),
            closure_summary=require_string(payload, "closure_summary"),
        )
    )
