import json
from pathlib import Path

from clauderfall.cli.main import app
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactRecord, Base


def test_validate_context_cli_accepts_valid_packet(runner, context_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(app, ["validate-context", str(context_json_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"valid": True, "issues": []}


def test_save_context_cli_persists_packet(runner, context_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(
        app,
        [
            "save-context",
            "context-1",
            str(context_json_path),
            "--upstream-ref",
            "task:task-1@1",
            "--upstream-ref",
            "design:design-1@1",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"saved": True, "artifact_id": "context-1", "version": 1}

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    record = session.get(ArtifactRecord, {"artifact_id": "context-1", "version": 1})

    assert record is not None
    assert record.artifact_kind == "context_packet"
    assert record.readiness_state == "ready"
    assert record.upstream_artifact_refs == ["task:task-1@1", "design:design-1@1"]


def test_validate_context_cli_rejects_invalid_packet(runner, context_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"
    packet = json.loads(context_json_path.read_text())
    packet["included_context"] = []
    invalid_path = tmp_path / "invalid-context.json"
    invalid_path.write_text(json.dumps(packet))

    result = runner.invoke(app, ["validate-context", str(invalid_path), "--db-path", str(db_path)])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["valid"] is False
    assert "included_context must not be empty" in payload["issues"]


def test_assemble_context_cli_outputs_packet(
    runner,
    task_json_path: Path,
    context_assembly_items_path: Path,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(
        app,
        ["assemble-context", str(task_json_path), str(context_assembly_items_path), "--db-path", str(db_path)],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["assembled"] is True
    assert payload["saved"] is False
    assert len(payload["packet"]["included_context"]) == 2


def test_assemble_context_cli_can_persist_packet(
    runner,
    task_json_path: Path,
    context_assembly_items_path: Path,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(
        app,
        [
            "assemble-context",
            str(task_json_path),
            str(context_assembly_items_path),
            "--artifact-id",
            "context-assembled-1",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["assembled"] is True
    assert payload["saved"] is True
    assert payload["artifact_id"] == "context-assembled-1"
    assert payload["version"] == 1


def test_assemble_context_from_refs_cli_loads_persisted_artifacts(
    runner,
    design_json_path: Path,
    task_json_path: Path,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "cli.db"

    runner.invoke(
        app,
        [
            "save-design",
            "design-1",
            str(design_json_path),
            "--upstream-ref",
            "discovery:disc-1@2",
            "--db-path",
            str(db_path),
        ],
    )
    runner.invoke(
        app,
        [
            "save-task",
            "task-1",
            str(task_json_path),
            "--upstream-ref",
            "design:design-1@1",
            "--db-path",
            str(db_path),
        ],
    )

    result = runner.invoke(
        app,
        [
            "assemble-context-from-refs",
            "task:task-1@1",
            "design:design-1@1",
            "--artifact-id",
            "context-assembled-2",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["assembled"] is True
    assert payload["saved"] is True
    assert payload["upstream_artifact_refs"] == ["task:task-1@1", "design:design-1@1"]
    assert payload["packet"]["included_context"][0]["source_origin"] == "design:design-1@1"


def test_query_trace_link_cli_returns_indexed_matches(
    runner,
    design_json_path: Path,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "cli.db"

    runner.invoke(
        app,
        [
            "save-design",
            "design-1",
            str(design_json_path),
            "--upstream-ref",
            "discovery:disc-1@2",
            "--db-path",
            str(db_path),
        ],
    )

    result = runner.invoke(
        app,
        [
            "query-trace-link",
            "discovery.problem_definition[0]",
            "--db-path",
            str(db_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["trace_link"] == "discovery.problem_definition[0]"
    assert payload["matches"][0]["artifact_id"] == "design-1"
    assert payload["matches"][0]["artifact_kind"] == "design"
