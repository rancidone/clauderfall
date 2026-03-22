"""Thin MCP tool adapter over the shared application services."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import IO
from typing import Any

from clauderfall.artifacts.common import ArtifactBase, ArtifactKind, ArtifactVersionRef
from clauderfall.artifacts.context import ContextPacket, ExclusionRecord
from clauderfall.artifacts.design import DesignArtifact
from clauderfall.artifacts.discovery import DiscoveryArtifact
from clauderfall.artifacts.task import TaskArtifact
from clauderfall.cli.main import build_artifact_service
from clauderfall.services.artifact_service import ArtifactService

class MCPToolDefinition(ArtifactBase):
    """Definition of one MCP-exposed tool."""

    name: str
    description: str
    inputSchema: dict[str, Any]


SUPPORTED_PROTOCOL_VERSIONS = (
    "2025-11-25",
    "2025-06-18",
    "2025-03-26",
)


class ClauderfallMCPServer:
    """Thin in-process MCP adapter over ArtifactService."""

    def __init__(self, artifact_service: ArtifactService) -> None:
        self._artifact_service = artifact_service

    def list_tools(self) -> list[MCPToolDefinition]:
        return [
            MCPToolDefinition(
                name="artifact.validate",
                description="Validate a candidate artifact body for one artifact kind.",
                inputSchema={
                    "type": "object",
                    "required": ["artifact_kind", "artifact_body"],
                    "properties": {
                        "artifact_kind": {"type": "string"},
                        "artifact_body": {"type": "object"},
                    },
                },
            ),
            MCPToolDefinition(
                name="artifact.get",
                description="Load an exact or latest persisted artifact version.",
                inputSchema={
                    "type": "object",
                    "required": ["artifact_kind", "artifact_id"],
                    "properties": {
                        "artifact_kind": {"type": "string"},
                        "artifact_id": {"type": "string"},
                        "version": {"type": "integer"},
                    },
                },
            ),
            MCPToolDefinition(
                name="contract.check_handoff",
                description="Check the next-stage handoff contract for a candidate artifact body.",
                inputSchema={
                    "type": "object",
                    "required": ["artifact_kind", "artifact_body"],
                    "properties": {
                        "artifact_kind": {"type": "string"},
                        "artifact_body": {"type": "object"},
                    },
                },
            ),
            MCPToolDefinition(
                name="context.assemble_from_refs",
                description="Assemble a context packet from persisted task and supporting artifact refs.",
                inputSchema={
                    "type": "object",
                    "required": ["task_ref", "supporting_refs"],
                    "properties": {
                        "task_ref": {"type": "object"},
                        "supporting_refs": {"type": "array"},
                        "exclusions": {"type": "array"},
                        "artifact_id": {"type": "string"},
                    },
                },
            ),
            MCPToolDefinition(
                name="traceability.get_links",
                description="Query persisted trace-link index rows.",
                inputSchema={
                    "type": "object",
                    "required": ["trace_link"],
                    "properties": {"trace_link": {"type": "string"}},
                },
            ),
            MCPToolDefinition(
                name="discovery.start_session",
                description="Load Discovery session state for an artifact lineage.",
                inputSchema={
                    "type": "object",
                    "required": ["artifact_id"],
                    "properties": {
                        "artifact_id": {"type": "string"},
                        "version": {"type": "integer"},
                    },
                },
            ),
            MCPToolDefinition(
                name="discovery.next_turn",
                description="Review one skill-authored Discovery turn against the current artifact lineage.",
                inputSchema={
                    "type": "object",
                    "required": ["artifact_id", "user_turn", "assistant_reply", "artifact_body"],
                    "properties": {
                        "artifact_id": {"type": "string"},
                        "user_turn": {"type": "string"},
                        "assistant_reply": {"type": "string"},
                        "artifact_body": {"type": "object"},
                        "version": {"type": "integer"},
                    },
                },
            ),
            MCPToolDefinition(
                name="discovery.save_revision",
                description="Persist a reviewed Discovery Artifact revision through the shared service layer.",
                inputSchema={
                    "type": "object",
                    "required": ["artifact_id", "artifact_body"],
                    "properties": {
                        "artifact_id": {"type": "string"},
                        "artifact_body": {"type": "object"},
                        "version": {"type": "integer"},
                    },
                },
            ),
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "artifact.validate": self._validate_artifact,
            "artifact.get": self._get_artifact,
            "contract.check_handoff": self._check_handoff,
            "context.assemble_from_refs": self._assemble_context_from_refs,
            "traceability.get_links": self._get_trace_links,
            "discovery.start_session": self._start_discovery_session,
            "discovery.next_turn": self._next_discovery_turn,
            "discovery.save_revision": self._save_discovery_revision,
        }
        try:
            handler = handlers[name]
        except KeyError as exc:
            raise ValueError(f"unknown MCP tool '{name}'") from exc
        return handler(arguments)

    def _validate_artifact(self, arguments: dict[str, Any]) -> dict[str, Any]:
        artifact_kind = self._parse_artifact_kind(arguments["artifact_kind"])
        artifact_body = arguments["artifact_body"]
        if artifact_kind is ArtifactKind.DISCOVERY:
            issues = self._artifact_service.validate_discovery(DiscoveryArtifact.model_validate(artifact_body))
        elif artifact_kind is ArtifactKind.DESIGN:
            issues = self._artifact_service.validate_design(DesignArtifact.model_validate(artifact_body))
        elif artifact_kind is ArtifactKind.TASK:
            issues = self._artifact_service.validate_task(TaskArtifact.model_validate(artifact_body))
        elif artifact_kind is ArtifactKind.CONTEXT_PACKET:
            issues = self._artifact_service.validate_context(ContextPacket.model_validate(artifact_body))
        else:
            raise ValueError(f"unsupported artifact kind for validation: {artifact_kind}")
        return {"valid": not issues, "issues": issues}

    def _get_artifact(self, arguments: dict[str, Any]) -> dict[str, Any]:
        artifact_kind = self._parse_artifact_kind(arguments["artifact_kind"])
        artifact_id = arguments["artifact_id"]
        version = arguments.get("version")
        if artifact_kind is ArtifactKind.DISCOVERY:
            artifact = self._artifact_service.load_discovery(artifact_id, version)
        elif artifact_kind is ArtifactKind.DESIGN:
            artifact = self._artifact_service.load_design(artifact_id, version)
        elif artifact_kind is ArtifactKind.TASK:
            artifact = self._artifact_service.load_task(artifact_id, version)
        elif artifact_kind is ArtifactKind.CONTEXT_PACKET:
            artifact = self._artifact_service.load_context(artifact_id, version)
        else:
            raise ValueError(f"unsupported artifact kind for get: {artifact_kind}")
        return {
            "found": artifact is not None,
            "artifact_kind": artifact_kind.value,
            "artifact_id": artifact_id,
            "version": version,
            "artifact_body": None if artifact is None else artifact.model_dump(mode="json"),
        }

    def _check_handoff(self, arguments: dict[str, Any]) -> dict[str, Any]:
        artifact_kind = self._parse_artifact_kind(arguments["artifact_kind"])
        artifact_body = arguments["artifact_body"]
        if artifact_kind is ArtifactKind.DISCOVERY:
            result = self._artifact_service.check_discovery_handoff(DiscoveryArtifact.model_validate(artifact_body))
        elif artifact_kind is ArtifactKind.DESIGN:
            result = self._artifact_service.check_design_handoff(DesignArtifact.model_validate(artifact_body))
        elif artifact_kind is ArtifactKind.TASK:
            result = self._artifact_service.check_task_handoff(TaskArtifact.model_validate(artifact_body))
        else:
            raise ValueError(f"handoff checks are not supported for artifact kind '{artifact_kind.value}'")
        return result.model_dump(mode="json")

    def _assemble_context_from_refs(self, arguments: dict[str, Any]) -> dict[str, Any]:
        task_ref = ArtifactVersionRef.model_validate(arguments["task_ref"])
        supporting_refs = [ArtifactVersionRef.model_validate(item) for item in arguments["supporting_refs"]]
        exclusions = None
        if "exclusions" in arguments and arguments["exclusions"] is not None:
            exclusions = [ExclusionRecord.model_validate(item) for item in arguments["exclusions"]]
        packet, upstream_artifact_refs = self._artifact_service.assemble_context_from_refs(
            task_ref=task_ref,
            supporting_refs=supporting_refs,
            exclusions=exclusions,
        )
        artifact_id = arguments.get("artifact_id")
        result = {
            "assembled": True,
            "saved": False,
            "upstream_artifact_refs": upstream_artifact_refs,
            "packet": packet.model_dump(mode="json"),
        }
        if artifact_id:
            version = self._artifact_service.save_context(
                artifact_id=artifact_id,
                packet=packet,
                upstream_artifact_refs=upstream_artifact_refs,
            )
            result.update({"saved": True, "artifact_id": artifact_id, "version": version})
        return result

    def _get_trace_links(self, arguments: dict[str, Any]) -> dict[str, Any]:
        trace_link = arguments["trace_link"]
        matches = self._artifact_service.query_trace_link(trace_link)
        return {
            "trace_link": trace_link,
            "matches": [match.model_dump(mode="json") for match in matches],
        }

    def _start_discovery_session(self, arguments: dict[str, Any]) -> dict[str, Any]:
        session = self._artifact_service.start_discovery_session(
            artifact_id=arguments["artifact_id"],
            version=arguments.get("version"),
        )
        return session.model_dump(mode="json")

    def _next_discovery_turn(self, arguments: dict[str, Any]) -> dict[str, Any]:
        result = self._artifact_service.next_discovery_turn(
            artifact_id=arguments["artifact_id"],
            user_turn=arguments["user_turn"],
            assistant_reply=arguments["assistant_reply"],
            candidate_artifact=DiscoveryArtifact.model_validate(arguments["artifact_body"]),
            version=arguments.get("version"),
        )
        return result.model_dump(mode="json")

    def _save_discovery_revision(self, arguments: dict[str, Any]) -> dict[str, Any]:
        artifact = DiscoveryArtifact.model_validate(arguments["artifact_body"])
        persisted_version, review = self._artifact_service.save_discovery_revision(
            artifact_id=arguments["artifact_id"],
            artifact=artifact,
            version=arguments.get("version"),
        )
        return {
            "saved": True,
            "artifact_id": arguments["artifact_id"],
            "version": persisted_version,
            "review": review.model_dump(mode="json"),
        }

    def _parse_artifact_kind(self, value: str) -> ArtifactKind:
        try:
            return ArtifactKind(value)
        except ValueError as exc:
            raise ValueError(f"unknown artifact kind '{value}'") from exc


def build_mcp_server(db_path: Path | None = None) -> ClauderfallMCPServer:
    """Build the thin MCP adapter over the shared ArtifactService."""

    return ClauderfallMCPServer(build_artifact_service(db_path=db_path))


class JSONRPCError(ArtifactBase):
    """JSON-RPC error payload."""

    code: int
    message: str


class ClauderfallMCPJSONRPCServer:
    """Newline-delimited JSON-RPC stdio transport for the MCP tool adapter."""

    def __init__(
        self,
        mcp_server: ClauderfallMCPServer,
        input_stream: IO[str],
        output_stream: IO[str],
        error_stream: IO[str],
    ) -> None:
        self._mcp_server = mcp_server
        self._input_stream = input_stream
        self._output_stream = output_stream
        self._error_stream = error_stream
        self._initialize_responded = False
        self._client_initialized = False
        self._shutdown_requested = False
        self._protocol_version = SUPPORTED_PROTOCOL_VERSIONS[0]

    def serve_forever(self) -> None:
        """Process newline-delimited JSON-RPC requests from stdio."""

        for raw_line in self._input_stream:
            line = raw_line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError:
                self._write_error_response(None, -32700, "parse error")
                continue

            if not isinstance(request, dict):
                self._write_error_response(None, -32600, "invalid request")
                continue

            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            if not isinstance(method, str):
                self._write_error_response(request_id, -32600, "invalid request")
                continue
            if params is None:
                params = {}
            if not isinstance(params, dict):
                self._write_error_response(request_id, -32602, "params must be an object")
                continue

            try:
                response = self._dispatch(method, params)
            except ValueError as exc:
                if request_id is not None:
                    self._write_error_response(request_id, -32602, str(exc))
                continue
            except Exception as exc:  # noqa: BLE001
                self._error_stream.write(f"clauderfall-mcp internal error: {exc}\n")
                self._error_stream.flush()
                if request_id is not None:
                    self._write_error_response(request_id, -32000, "internal server error")
                continue

            if request_id is not None and response is not None:
                self._write_response(request_id, response)

            if method == "exit":
                return

    def _dispatch(self, method: str, params: dict[str, Any]) -> dict[str, Any] | None:
        if method == "initialize":
            requested_version = params.get("protocolVersion")
            self._protocol_version = self._negotiate_protocol_version(requested_version)
            self._initialize_responded = True
            return {
                "protocolVersion": self._protocol_version,
                "serverInfo": {"name": "clauderfall", "title": "Clauderfall", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            }
        if method == "ping":
            return {"pong": True}
        if method == "notifications/initialized":
            if not self._initialize_responded:
                raise ValueError("server must respond to 'initialize' before 'notifications/initialized'")
            self._client_initialized = True
            return None
        if method.startswith("notifications/"):
            return None
        if method == "shutdown":
            self._shutdown_requested = True
            return {"shutdown": True}
        if method == "exit":
            return {"exit": True}
        if not self._initialize_responded:
            raise ValueError("server must be initialized before calling other methods")
        if not self._client_initialized:
            raise ValueError("client must send 'notifications/initialized' before calling other methods")
        if self._shutdown_requested and method != "exit":
            raise ValueError("server is shut down; only 'exit' is allowed")
        if method == "tools/list":
            return {"tools": [tool.model_dump(mode="json") for tool in self._mcp_server.list_tools()]}
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(tool_name, str):
                raise ValueError("tools/call requires string field 'name'")
            if not isinstance(arguments, dict):
                raise ValueError("tools/call requires object field 'arguments'")
            result = self._mcp_server.call_tool(tool_name, arguments)
            return {
                "content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}],
                "structuredContent": result,
                "isError": False,
            }
        raise ValueError(f"unknown method '{method}'")

    def _negotiate_protocol_version(self, requested_version: Any) -> str:
        if isinstance(requested_version, str) and requested_version in SUPPORTED_PROTOCOL_VERSIONS:
            return requested_version
        return SUPPORTED_PROTOCOL_VERSIONS[0]

    def _write_response(self, request_id: Any, result: dict[str, Any]) -> None:
        payload = {"jsonrpc": "2.0", "id": request_id, "result": result}
        self._output_stream.write(json.dumps(payload) + "\n")
        self._output_stream.flush()

    def _write_error_response(self, request_id: Any, code: int, message: str) -> None:
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": JSONRPCError(code=code, message=message).model_dump(mode="json"),
        }
        self._output_stream.write(json.dumps(payload) + "\n")
        self._output_stream.flush()


def run_stdio_server(db_path: Path | None = None) -> None:
    """Run the newline-delimited JSON-RPC stdio server."""

    transport = ClauderfallMCPJSONRPCServer(
        mcp_server=build_mcp_server(db_path=db_path),
        input_stream=sys.stdin,
        output_stream=sys.stdout,
        error_stream=sys.stderr,
    )
    transport.serve_forever()


def main() -> None:
    """Entrypoint for the stdio MCP server."""

    run_stdio_server()
