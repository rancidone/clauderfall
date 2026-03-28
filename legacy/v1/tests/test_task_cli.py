import json
from pathlib import Path

from clauderfall_v1.cli.main import app
from clauderfall_v1.persistence.db import create_session_factory
from clauderfall_v1.persistence.models import ArtifactRecord, Base


def test_validate_task_cli_accepts_valid_artifact(runner, task_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(app, ["validate-task", str(task_json_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"valid": True, "issues": []}


def test_save_task_cli_persists_artifact(runner, task_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(
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

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"saved": True, "artifact_id": "task-1", "version": 1}

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    record = session.get(ArtifactRecord, {"artifact_id": "task-1", "version": 1})

    assert record is not None
    assert record.artifact_kind == "task"
    assert record.readiness_state == "ready"
    assert record.upstream_artifact_refs == ["design:design-1@1"]


def test_check_task_handoff_cli_reports_failure(runner, task_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"
    artifact = json.loads(task_json_path.read_text())
    artifact["completion_status"]["readiness_state"] = "not_ready"
    artifact["completion_status"]["blocking_gaps"] = ["Need concrete acceptance criteria."]
    invalid_path = tmp_path / "not-ready-task.json"
    invalid_path.write_text(json.dumps(artifact))

    result = runner.invoke(app, ["check-task-handoff", str(invalid_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["accepted"] is False
    assert "completion_status.readiness_state must be 'ready' before Context can begin" in payload["reasons"]
