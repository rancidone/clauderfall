import io
import json
from pathlib import Path

from clauderfall.artifacts.common import ArtifactKind
from clauderfall.mcp.server import ClauderfallMCPJSONRPCServer, build_mcp_server


def test_mcp_server_lists_expected_tools(tmp_path: Path) -> None:
    server = build_mcp_server(db_path=tmp_path / "mcp.db")

    tools = server.list_tools()
    tool_names = {tool.name for tool in tools}

    assert "artifact.validate" in tool_names
    assert "artifact.get" in tool_names
    assert "contract.check_handoff" in tool_names
    assert "discovery.prepare_turn" in tool_names
    assert "discovery.propose_revision" in tool_names
    assert "context.assemble_from_refs" in tool_names
    assert "traceability.get_links" in tool_names


def test_mcp_server_can_validate_and_get_discovery_artifact(
    tmp_path: Path,
    valid_discovery_artifact,
) -> None:
    server = build_mcp_server(db_path=tmp_path / "mcp.db")

    validate_result = server.call_tool(
        "artifact.validate",
        {
            "artifact_kind": ArtifactKind.DISCOVERY.value,
            "artifact_body": valid_discovery_artifact.model_dump(mode="json"),
        },
    )
    server.call_tool(
        "discovery.save_revision",
        {
            "artifact_id": "disc-1",
            "artifact_body": valid_discovery_artifact.model_dump(mode="json"),
        },
    )
    get_result = server.call_tool(
        "artifact.get",
        {
            "artifact_kind": ArtifactKind.DISCOVERY.value,
            "artifact_id": "disc-1",
            "version": 1,
        },
    )

    assert validate_result == {"valid": True, "issues": []}
    assert get_result["found"] is True
    assert get_result["artifact_kind"] == "discovery"
    assert get_result["artifact_body"]["problem_definition"] == valid_discovery_artifact.problem_definition


def test_mcp_server_supports_discovery_turn_and_proposal(
    tmp_path: Path,
    discovery_proposal,
) -> None:
    server = build_mcp_server(db_path=tmp_path / "mcp.db")

    prepare_result = server.call_tool(
        "discovery.prepare_turn",
        {
            "artifact_id": "disc-1",
            "user_turn": "We need measurable success criteria and explicit scope.",
        },
    )
    proposal_result = server.call_tool(
        "discovery.propose_revision",
        {
            "artifact_id": "disc-1",
            "user_turn": "We need measurable success criteria and explicit scope.",
            "proposal": discovery_proposal.model_dump(mode="json"),
        },
    )

    assert prepare_result["session"]["skill_name"] == "discovery"
    assert "You are the Discovery driver for Clauderfall." in prepare_result["skill_instructions"]
    assert proposal_result["proposal"]["assistant_reply"].startswith("I tightened the discovery draft")
    assert proposal_result["review"]["persistable"] is True


def test_mcp_server_can_query_trace_links_and_assemble_context_from_refs(
    tmp_path: Path,
    valid_design_artifact,
    valid_task_artifact,
) -> None:
    server = build_mcp_server(db_path=tmp_path / "mcp.db")

    server.call_tool(
        "discovery.save_revision",
        {
            "artifact_id": "disc-1",
            "artifact_body": {
                "problem_definition": ["Agents need bounded context."],
                "constraints": ["Context must remain traceable."],
                "success_criteria": ["Discovery can be handed to design."],
                "scope_boundaries": {"in_scope": ["Discovery"], "out_of_scope": ["Execution"], "boundary_notes": []},
                "risks": ["Terminology drift."],
                "unknowns": ["Whether MCP should expose transport now."],
                "open_questions": ["Do we need transport now or later?"],
                "source_register": [{"source_id": "src-1", "source_type": "doc", "origin_ref": "prompt"}],
                "provenance_records": [
                    {
                        "target_ref": target,
                        "source_classification": "explicit",
                        "confidence": "high",
                        "grounding": "anchored",
                        "trace_links": ["src-1"],
                    }
                    for target in [
                        "problem_definition",
                        "constraints",
                        "success_criteria",
                        "scope_boundaries",
                        "risks",
                        "unknowns",
                        "open_questions",
                    ]
                ],
                "completion_status": {
                    "readiness_state": "ready",
                    "blocking_gaps": [],
                    "non_blocking_gaps": [],
                    "justification": "Grounded enough for design.",
                },
            },
        },
    )
    server.call_tool(
        "discovery.save_revision",
        {
            "artifact_id": "disc-x",
            "artifact_body": {
                "problem_definition": ["placeholder"],
                "constraints": ["placeholder"],
                "success_criteria": ["placeholder"],
                "scope_boundaries": {"in_scope": ["placeholder"], "out_of_scope": [], "boundary_notes": []},
                "risks": ["placeholder"],
                "unknowns": ["placeholder"],
                "open_questions": ["placeholder"],
                "source_register": [{"source_id": "src-2", "source_type": "doc", "origin_ref": "placeholder"}],
                "provenance_records": [
                    {
                        "target_ref": target,
                        "source_classification": "explicit",
                        "confidence": "high",
                        "grounding": "anchored",
                        "trace_links": ["src-2"],
                    }
                    for target in [
                        "problem_definition",
                        "constraints",
                        "success_criteria",
                        "scope_boundaries",
                        "risks",
                        "unknowns",
                        "open_questions",
                    ]
                ],
                "completion_status": {
                    "readiness_state": "ready",
                    "blocking_gaps": [],
                    "non_blocking_gaps": [],
                    "justification": "placeholder",
                },
            },
        },
    )
    server._artifact_service.save_design(  # noqa: SLF001
        artifact_id="design-1",
        artifact=valid_design_artifact,
        upstream_artifact_refs=["discovery:disc-1@1"],
    )
    server._artifact_service.save_task(  # noqa: SLF001
        artifact_id="task-1",
        artifact=valid_task_artifact,
        upstream_artifact_refs=["design:design-1@1"],
    )

    trace_result = server.call_tool(
        "traceability.get_links",
        {"trace_link": "discovery.problem_definition[0]"},
    )
    assemble_result = server.call_tool(
        "context.assemble_from_refs",
        {
            "task_ref": {"artifact_kind": "task", "artifact_id": "task-1", "version": 1},
            "supporting_refs": [
                {"artifact_kind": "design", "artifact_id": "design-1", "version": 1},
            ],
            "artifact_id": "context-1",
        },
    )

    assert trace_result["matches"][0]["artifact_id"] == "design-1"
    assert assemble_result["assembled"] is True
    assert assemble_result["saved"] is True
    assert assemble_result["artifact_id"] == "context-1"
    assert assemble_result["upstream_artifact_refs"] == ["task:task-1@1", "design:design-1@1"]


def test_mcp_jsonrpc_stdio_handles_initialize_list_and_call(
    tmp_path: Path,
    valid_discovery_artifact,
) -> None:
    server = build_mcp_server(db_path=tmp_path / "mcp.db")
    input_stream = io.StringIO(
        "\n".join(
            [
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "artifact.validate",
                            "arguments": {
                                "artifact_kind": "discovery",
                                "artifact_body": valid_discovery_artifact.model_dump(mode="json"),
                            },
                        },
                    }
                ),
                json.dumps({"jsonrpc": "2.0", "id": 4, "method": "shutdown", "params": {}}),
                json.dumps({"jsonrpc": "2.0", "id": 5, "method": "exit", "params": {}}),
                "",
            ]
        )
    )
    output_stream = io.StringIO()
    error_stream = io.StringIO()

    transport = ClauderfallMCPJSONRPCServer(server, input_stream, output_stream, error_stream)
    transport.serve_forever()

    responses = [json.loads(line) for line in output_stream.getvalue().splitlines() if line.strip()]
    assert responses[0]["result"]["serverInfo"]["name"] == "clauderfall"
    assert any(tool["name"] == "artifact.validate" for tool in responses[1]["result"]["tools"])
    assert responses[2]["result"]["content"] == {"valid": True, "issues": []}
    assert responses[3]["result"] == {"shutdown": True}
    assert responses[4]["result"] == {"exit": True}
    assert error_stream.getvalue() == ""


def test_mcp_jsonrpc_stdio_rejects_calls_before_initialize(tmp_path: Path) -> None:
    server = build_mcp_server(db_path=tmp_path / "mcp.db")
    input_stream = io.StringIO(
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}) + "\n"
    )
    output_stream = io.StringIO()
    error_stream = io.StringIO()

    transport = ClauderfallMCPJSONRPCServer(server, input_stream, output_stream, error_stream)
    transport.serve_forever()

    response = json.loads(output_stream.getvalue().strip())
    assert response["error"]["code"] == -32602
    assert "initialized" in response["error"]["message"]
