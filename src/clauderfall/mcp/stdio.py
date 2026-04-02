"""Minimal stdio MCP transport for the Clauderfall tool surface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from clauderfall import __version__, debug_log
from clauderfall.mcp import create_server


PROTOCOL_VERSION = "2025-06-18"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Clauderfall MCP server over stdio.")
    parser.add_argument("--repo-root", default=".", help="Repository root to expose through runtime-backed tools.")
    parser.add_argument(
        "--docs-root",
        default=None,
        help="Optional docs root. Relative paths are resolved under --repo-root. Default: docs",
    )
    args = parser.parse_args()

    server = create_server(
        Path(args.repo_root).resolve(),
        args.docs_root,
    )
    initialized = False

    debug_log.info("stdio server started repo_root=%s", Path(args.repo_root).resolve())
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        debug_log.debug("recv: %s", line[:500])
        response, initialized = _handle_message(server=server, initialized=initialized, raw_message=line)
        if response is None:
            continue
        encoded = json.dumps(response, separators=(",", ":"))
        debug_log.debug("send: %s", encoded[:500])
        sys.stdout.write(encoded + "\n")
        sys.stdout.flush()
    debug_log.info("stdio server stdin closed, exiting")
    return 0


def _handle_message(*, server, initialized: bool, raw_message: str) -> tuple[dict[str, Any] | None, bool]:
    try:
        message = json.loads(raw_message)
    except json.JSONDecodeError:
        return _error_response(None, -32700, "parse error"), initialized

    if not isinstance(message, dict):
        return _error_response(None, -32600, "invalid request"), initialized

    if message.get("jsonrpc") != "2.0":
        return _error_response(message.get("id"), -32600, "invalid request"), initialized

    method = message.get("method")
    params = message.get("params", {})
    request_id = message.get("id")
    is_notification = request_id is None

    if not isinstance(method, str):
        return _error_response(request_id, -32600, "invalid request"), initialized
    if not isinstance(params, dict):
        return _error_response(request_id, -32602, "invalid params"), initialized

    if method == "initialize":
        return (
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": "clauderfall",
                        "title": "Clauderfall MCP Server",
                        "version": __version__,
                    },
                    "instructions": "Use the flat Clauderfall tools to read and mutate runtime-backed Discovery, Design, and session lifecycle state.",
                },
            },
            initialized,
        )

    if method == "notifications/initialized":
        return None, True

    if not initialized:
        return _error_response(request_id, -32002, "server not initialized"), initialized

    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}, initialized

    if method == "tools/list":
        tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
            }
            for tool in server.list_tools()
        ]
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}, initialized

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str):
            return _error_response(request_id, -32602, "invalid params"), initialized
        if not isinstance(arguments, dict):
            return _error_response(request_id, -32602, "invalid params"), initialized
        if not server.has_tool(name):
            return _error_response(request_id, -32602, f"unknown tool: {name}"), initialized

        tool_result = server.call_tool(name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_result, separators=(",", ":"), sort_keys=True),
                    }
                ],
                "structuredContent": tool_result,
                "isError": tool_result["result"] == "failure",
            },
        }, initialized

    if is_notification:
        return None, initialized

    return _error_response(request_id, -32601, f"method not found: {method}"), initialized


def _error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
