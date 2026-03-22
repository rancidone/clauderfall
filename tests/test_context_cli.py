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

    result = runner.invoke(app, ["save-context", "context-1", str(context_json_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"saved": True, "artifact_id": "context-1", "version": 1}

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    record = session.get(ArtifactRecord, {"artifact_id": "context-1", "version": 1})

    assert record is not None
    assert record.artifact_kind == "context_packet"
    assert record.readiness_state == "ready"


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
