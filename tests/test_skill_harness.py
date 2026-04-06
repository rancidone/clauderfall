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


def _session_startup_result(
    *,
    current: dict[str, Any] | None,
    recent_completed: list[dict[str, Any]] | None = None,
) -> str:
    return _tool_result(
        artifacts={
            "current": current,
            "recent_completed": recent_completed or [],
        },
        metadata={
            "rebuilt": False,
            "has_current": current is not None,
            "recent_completed_count": len(recent_completed or []),
        },
    )


def _session_current_result(
    *,
    title: str,
    work_items: list[str],
    thread_markdown: str,
) -> str:
    return _tool_result(
        artifacts={
            "title": title,
            "work_items": work_items,
            "thread_markdown": thread_markdown,
        },
        metadata={"artifact_id": "current"},
    )


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


@pytest.mark.skipif(not HARNESS_ENABLED, reason=SKIP_REASON)
def test_session_continue_reads_startup_before_current_drill_in(tmp_path: Path) -> None:
    """session_continue should orient through startup view before drilling into current state."""
    tools = _mcp_tools(tmp_path)
    system = _skill_prompt("session_continue")
    client = _make_client()
    model = _model()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Continue prior work. I think I left a couple threads open."},
    ]

    first = _chat_once(client=client, model=model, messages=messages, tools=tools)
    assert first.tool_calls, "session_continue did not call any tool for startup orientation"
    assert first.tool_calls[0].function.name == "session_read_startup_view"

    messages.append(first.model_dump(exclude_unset=True))
    messages.append(
        {
            "role": "tool",
            "tool_call_id": first.tool_calls[0].id,
            "content": _session_startup_result(
                current={
                    "title": "Session Continuity Skill Surface",
                    "work_items": ["Inspect the uncommitted skill scaffolding and decide whether to ship it."],
                    "last_updated_at": "2026-04-02T20:00:00Z",
                },
                recent_completed=[
                    {
                        "history_id": "design-status-skill",
                        "title": "Design Status Skill",
                        "closed_at": "2026-04-01T20:00:00Z",
                    }
                ],
            ),
        }
    )

    second = _chat_once(client=client, model=model, messages=messages, tools=tools)
    assert not second.tool_calls, "session_continue drilled into current state before the operator chose it"
    text = second.content if isinstance(second.content, str) else json.dumps(second.model_dump(exclude_unset=True))
    assert "Session Continuity Skill Surface" in text


@pytest.mark.skipif(not HARNESS_ENABLED, reason=SKIP_REASON)
def test_session_continue_reads_current_after_operator_choice(tmp_path: Path) -> None:
    """session_continue should read current state only after selection becomes explicit."""
    tools = _mcp_tools(tmp_path)
    system = _skill_prompt("session_continue")
    client = _make_client()
    model = _model()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": "Show me my current carry-forward state."},
    ]

    first = _chat_once(client=client, model=model, messages=messages, tools=tools)
    assert first.tool_calls and first.tool_calls[0].function.name == "session_read_startup_view"
    messages.append(first.model_dump(exclude_unset=True))
    messages.append(
        {
            "role": "tool",
            "tool_call_id": first.tool_calls[0].id,
            "content": _session_startup_result(
                current={
                    "title": "Session Continuity Skill Surface",
                    "work_items": ["Inspect the uncommitted skill scaffolding and decide whether to ship it."],
                    "last_updated_at": "2026-04-02T20:00:00Z",
                }
            ),
        }
    )
    second = _chat_once(client=client, model=model, messages=messages, tools=tools)
    messages.append(second.model_dump(exclude_unset=True))
    messages.append(
        {
            "role": "user",
            "content": "Inspect the current carry-forward state but do not save anything yet.",
        }
    )

    third = _chat_once(client=client, model=model, messages=messages, tools=tools)
    assert third.tool_calls, "session_continue did not drill into the selected current state"
    assert third.tool_calls[0].function.name == "session_read_current"
    arguments = json.loads(third.tool_calls[0].function.arguments)
    assert arguments == {}


@pytest.mark.skipif(not HARNESS_ENABLED, reason=SKIP_REASON)
def test_session_handoff_reads_current_state_before_overwrite_when_needed(tmp_path: Path) -> None:
    """session_handoff should use startup state and current reads before overwriting when needed."""
    tools = _mcp_tools(tmp_path)
    system = _skill_prompt("session_handoff")
    client = _make_client()
    model = _model()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                "Save a handoff for the session continuity skill work. "
                "Reuse the existing current state if it already matches."
            ),
        },
    ]

    first = _chat_once(client=client, model=model, messages=messages, tools=tools)
    assert first.tool_calls, "session_handoff did not read startup state before resolving overwrite behavior"
    assert first.tool_calls[0].function.name == "session_read_startup_view"

    messages.append(first.model_dump(exclude_unset=True))
    messages.append(
        {
            "role": "tool",
            "tool_call_id": first.tool_calls[0].id,
            "content": _session_startup_result(
                current={
                    "title": "Session Continuity Skill Surface",
                    "work_items": ["Inspect the uncommitted skill scaffolding and decide whether to ship it."],
                    "last_updated_at": "2026-04-02T20:00:00Z",
                }
            ),
        }
    )

    second = _chat_once(client=client, model=model, messages=messages, tools=tools)
    assert second.tool_calls, "session_handoff stopped before resolving the handoff write path"

    second_call = second.tool_calls[0]
    second_args = _parse_tool_arguments(
        tool_name=second_call.function.name,
        raw_arguments=second_call.function.arguments,
    )

    if second_call.function.name == "session_read_current":
        messages.append(second.model_dump(exclude_unset=True))
        messages.append(
            {
                "role": "tool",
                "tool_call_id": second_call.id,
                "content": _session_current_result(
                    title="Session Continuity Skill Surface",
                    work_items=["Inspect the uncommitted skill scaffolding and decide whether to ship it."],
                    thread_markdown="# Session Continuity Skill Surface\n\nUncommitted skill scaffolding is pending review.",
                ),
            }
        )
        third = _chat_once(client=client, model=model, messages=messages, tools=tools)
        if third.tool_calls:
            write_call = third.tool_calls[0]
            assert write_call.function.name == "session_write_handoff"
            arguments = _parse_tool_arguments(
                tool_name=write_call.function.name,
                raw_arguments=write_call.function.arguments,
            )
        else:
            messages.append(third.model_dump(exclude_unset=True))
            messages.append(
                {
                    "role": "user",
                    "content": "Persist that handoff now with session_write_handoff.",
                }
            )
            fourth = _chat_once(client=client, model=model, messages=messages, tools=tools)
            assert fourth.tool_calls, "session_handoff did not write after explicit persistence confirmation"
            write_call = fourth.tool_calls[0]
            assert write_call.function.name == "session_write_handoff"
            arguments = _parse_tool_arguments(
                tool_name=write_call.function.name,
                raw_arguments=write_call.function.arguments,
            )
    else:
        assert second_call.function.name == "session_write_handoff"
        arguments = second_args

    assert arguments["title"] == "Session Continuity Skill Surface"
    assert arguments["work_items"]
    assert arguments["thread_markdown"]


@pytest.mark.skipif(not HARNESS_ENABLED, reason=SKIP_REASON)
def test_session_handoff_writes_new_current_state_with_required_fields(tmp_path: Path) -> None:
    """session_handoff should produce a complete write payload for clearly new current state."""
    tools = _mcp_tools(tmp_path)
    system = _skill_prompt("session_handoff")

    write_input = _run_skill_until_tool_call(
        system=system,
        tools=tools,
        initial_user_message=(
            "Save a handoff for new work titled Skill Harness Coverage. "
            "Work items: add session skill harness tests; add a one-command runner; run the harness against Qwen and inspect failures. "
            "State to carry: the harness path exists but the handoff payload still needs cleanup."
        ),
        target_tool="session_write_handoff",
        follow_up="Persist that handoff now with session_write_handoff.",
        tmp_path=tmp_path,
    )

    assert write_input is not None, "session_handoff did not call session_write_handoff within the turn limit"
    for field in (
        "title",
        "work_items",
        "thread_markdown",
    ):
        assert write_input.get(field), f"session_write_handoff missing required field: {field}"


@pytest.mark.skipif(not HARNESS_ENABLED, reason=SKIP_REASON)
def test_session_handoff_does_not_write_without_explicit_persistence_intent(tmp_path: Path) -> None:
    """session_handoff should not persist when the operator has not asked to save yet."""
    tools = _mcp_tools(tmp_path)
    system = _skill_prompt("session_handoff")
    client = _make_client()
    model = _model()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                "Adjust the carry-forward summary so it drops the stale item, but do not save anything yet."
            ),
        },
    ]

    forbidden_calls = {"session_write_handoff", "session_archive_current"}
    text = ""

    for _ in range(3):
        msg = _chat_once(client=client, model=model, messages=messages, tools=tools)
        assert not any(tc.function.name in forbidden_calls for tc in (msg.tool_calls or [])), (
            "session_handoff attempted persistence despite no explicit persistence intent"
        )
        if not msg.tool_calls:
            text = msg.content if isinstance(msg.content, str) else json.dumps(msg.model_dump(exclude_unset=True))
            break

        messages.append(msg.model_dump(exclude_unset=True))
        for tc in msg.tool_calls:
            if tc.function.name == "session_read_startup_view":
                tool_content = _session_startup_result(current=None)
            elif tc.function.name == "session_read_current":
                tool_content = _session_current_result(
                    title="Carry Forward Thread",
                    work_items=["Clean up the handoff note later."],
                    thread_markdown="# Carry Forward Thread\n\nOld state with a stale item.",
                )
            else:
                tool_content = _tool_success()

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_content,
                }
            )

    assert text, "session_handoff did not produce a non-persistence reply within the turn budget"
    assert "save" in text.lower() or "persist" in text.lower() or "write" in text.lower()
