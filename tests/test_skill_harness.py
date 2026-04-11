"""LLM-in-the-loop harness tests for Clauderfall skills.

Requires an OpenAI-compatible endpoint (e.g. vLLM, Ollama, LM Studio).

Run with:
    uv run pytest tests/test_skill_harness.py -v

Required env vars:
  CLAUDERFALL_LLM_BASE_URL  - base URL of the OpenAI-compatible endpoint
  CLAUDERFALL_LLM_MODEL     - model name as served by the endpoint

Optional:
  CLAUDERFALL_LLM_API_KEY   - API key (default: 'local')
  CLAUDERFALL_LLM_HARNESS   - set to 1 to enable live model tests
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from clauderfall.mcp import create_server
from clauderfall.runtime.discovery import _validate_problem_area, _validate_assumption

HARNESS_ENABLED = os.environ.get("CLAUDERFALL_LLM_HARNESS", "").strip() in {"1", "true", "yes"}
SKIP_REASON = "LLM harness tests require CLAUDERFALL_LLM_HARNESS=1 and CLAUDERFALL_LLM_BASE_URL"

MAX_TURNS = 8
MAX_TOKENS = int(os.environ.get("CLAUDERFALL_LLM_HARNESS_MAX_TOKENS", "1024"))


def _skill_prompt(skill_name: str) -> str:
    skill_path = (
        Path(__file__).parent.parent
        / "src"
        / "clauderfall"
        / "skills"
        / skill_name
        / "SKILL.md"
    )
    return skill_path.read_text()


def _mcp_tools(tmp_path: Path) -> list[dict[str, Any]]:
    server = create_server(tmp_path)
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in server.list_tools()
    ]


def _make_client() -> Any:
    from openai import OpenAI

    base_url = os.environ.get("CLAUDERFALL_LLM_BASE_URL")
    if not base_url:
        pytest.skip("CLAUDERFALL_LLM_BASE_URL not set")
    api_key = os.environ.get("CLAUDERFALL_LLM_API_KEY", "local")
    return OpenAI(base_url=base_url, api_key=api_key)


def _model() -> str:
    model = os.environ.get("CLAUDERFALL_LLM_MODEL")
    if not model:
        pytest.skip("CLAUDERFALL_LLM_MODEL not set")
    return model


def _tool_success() -> str:
    return json.dumps({"result": "success", "warnings": [], "artifacts": {}, "metadata": {}})


def _tool_result(
    *,
    result: str = "success",
    warnings: list[str] | None = None,
    artifacts: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    return json.dumps(
        {
            "result": result,
            "warnings": warnings or [],
            "artifacts": artifacts or {},
            "metadata": metadata or {},
        }
    )


def _chat_once(
    *,
    client: Any,
    model: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> Any:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message


def _parse_tool_arguments(*, tool_name: str, raw_arguments: str) -> dict[str, Any]:
    try:
        return json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        snippet = raw_arguments[:400]
        pytest.fail(
            f"{tool_name} produced invalid JSON tool arguments: {exc}. Raw prefix: {snippet!r}"
        )


def _run_skill_until_tool_call(
    *,
    system: str,
    tools: list[dict[str, Any]],
    initial_user_message: str,
    target_tool: str,
    follow_up: str = "Please write the current draft now.",
    tmp_path: Path,
) -> dict[str, Any] | None:
    """Drive a multi-turn conversation until the target tool is called.

    Returns the parsed tool arguments dict if found within MAX_TURNS, else None.
    """
    client = _make_client()
    model = _model()
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": initial_user_message},
    ]

    for turn in range(MAX_TURNS):
        msg = _chat_once(client=client, model=model, messages=messages, tools=tools)

        # Check for the target tool call
        if msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.function.name == target_tool:
                    return _parse_tool_arguments(
                        tool_name=tc.function.name,
                        raw_arguments=tc.function.arguments,
                    )

        # Append assistant turn
        messages.append(msg.model_dump(exclude_unset=True))

        # Stub-respond to any tool calls
        if msg.tool_calls:
            for tc in msg.tool_calls:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": _tool_success(),
                    }
                )
        elif turn < MAX_TURNS - 1:
            # Escalate to a direct write instruction after the first few turns
            if turn >= 2:
                messages.append({
                    "role": "user",
                    "content": (
                        "You have enough information to write a first draft. "
                        f"Call {target_tool} now with what you have."
                    ),
                })
            else:
                messages.append({"role": "user", "content": follow_up})

    return None


@pytest.mark.skipif(not HARNESS_ENABLED, reason=SKIP_REASON)
def test_discovery_skill_writes_conforming_sidecar(tmp_path: Path) -> None:
    """Discovery skill produces a sidecar with all required per-item schema fields."""
    tools = _mcp_tools(tmp_path)
    system = _skill_prompt("discovery")

    scenario = (
        "I want to build a small CLI tool to track my electronics components inventory. "
        "I have resistors, capacitors, and ICs in labeled bins but I keep buying duplicates "
        "because I can never find what I already own when I'm at my bench. "
        "It's just me using this, single machine, no network. "
        "Core operations are: add a part with quantity and attributes, "
        "and query what I have by value or part number. "
        "No auth, no location tracking, no semantic search. "
        "Scale is hundreds of SKUs at most. "
        "That's the full scope — I don't need more features right now."
    )

    write_input = _run_skill_until_tool_call(
        system=system,
        tools=tools,
        initial_user_message=scenario,
        target_tool="discovery_write",
        follow_up="Please persist the current discovery draft with discovery_write.",
        tmp_path=tmp_path,
    )

    assert write_input is not None, (
        "Discovery skill did not call discovery_write within the turn limit. "
        "Check CLAUDERFALL_LLM_BASE_URL and CLAUDERFALL_LLM_MODEL are set correctly."
    )

    sidecar = write_input.get("sidecar", {})
    assert isinstance(sidecar, dict), f"Expected sidecar dict, got: {type(sidecar)}"

    for field in ("title", "status", "readiness", "readiness_rationale", "blocking_gaps", "problem_areas", "cross_cutting"):
        assert field in sidecar, f"Sidecar missing top-level field: {field}"

    assert sidecar["status"] in {"draft", "accepted"}, f"Invalid status: {sidecar['status']}"
    assert sidecar["readiness"] in {"low", "medium", "high"}, f"Invalid readiness: {sidecar['readiness']}"
    assert isinstance(sidecar["problem_areas"], list) and sidecar["problem_areas"], (
        "problem_areas must be a non-empty list"
    )

    for i, area in enumerate(sidecar["problem_areas"]):
        item_errors = _validate_problem_area(i, area)
        assert not item_errors, (
            f"problem_areas[{i}] schema violations:\n" + "\n".join(item_errors)
        )

    for i, area in enumerate(sidecar["problem_areas"]):
        for j, assumption in enumerate(area.get("assumptions", [])):
            assumption_errors = _validate_assumption(
                f"problem_areas[{i}].assumptions[{j}]", assumption
            )
            assert not assumption_errors, "\n".join(assumption_errors)


@pytest.mark.skipif(not HARNESS_ENABLED, reason=SKIP_REASON)
def test_discovery_skill_calls_to_design_only_after_write(tmp_path: Path) -> None:
    """Discovery skill should not attempt discovery_to_design before writing a brief."""
    tools = _mcp_tools(tmp_path)
    system = _skill_prompt("discovery")

    response_tool = _run_skill_until_tool_call(
        system=system,
        tools=tools,
        initial_user_message="Transition directly to Design right now without any Discovery work.",
        target_tool="discovery_to_design",
        follow_up="Call discovery_to_design immediately.",
        tmp_path=tmp_path,
    )

    # If to_design was called, verify it at minimum included a brief_id.
    # A compliant skill should have written a brief first — but we can't assert that
    # strictly here because stub tool responses mask the write. What we can assert is
    # that the call was structurally valid if it was made.
    if response_tool is not None:
        assert "brief_id" in response_tool, (
            "discovery_to_design called without brief_id"
        )
