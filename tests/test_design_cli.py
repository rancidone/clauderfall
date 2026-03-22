import json
from pathlib import Path

from clauderfall.cli.main import app
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactRecord, Base


def test_validate_design_cli_accepts_valid_artifact(runner, design_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(app, ["validate-design", str(design_json_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"valid": True, "issues": []}


def test_save_design_cli_persists_artifact(runner, design_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(app, ["save-design", "design-1", str(design_json_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"saved": True, "artifact_id": "design-1", "version": 1}

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    record = session.get(ArtifactRecord, {"artifact_id": "design-1", "version": 1})

    assert record is not None
    assert record.artifact_kind == "design"
    assert record.readiness_state == "ready"


def test_check_design_handoff_cli_reports_failure(runner, design_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"
    artifact = json.loads(design_json_path.read_text())
    artifact["completion_status"]["readiness_state"] = "not_ready"
    artifact["completion_status"]["blocking_gaps"] = ["Need stronger task decomposition signals."]
    invalid_path = tmp_path / "not-ready-design.json"
    invalid_path.write_text(json.dumps(artifact))

    result = runner.invoke(app, ["check-design-handoff", str(invalid_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["accepted"] is False
    assert "completion_status.readiness_state must be 'ready' before Task can begin" in payload["reasons"]
