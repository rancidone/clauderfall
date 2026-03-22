import json
from pathlib import Path

from clauderfall.cli.main import app
from clauderfall.persistence.db import create_session_factory
from clauderfall.persistence.models import ArtifactRecord, Base


def test_validate_discovery_cli_accepts_valid_artifact(runner, discovery_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(app, ["validate-discovery", str(discovery_json_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"valid": True, "issues": []}


def test_validate_discovery_cli_rejects_invalid_artifact(runner, discovery_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"
    artifact = json.loads(discovery_json_path.read_text())
    artifact["success_criteria"] = []
    invalid_path = tmp_path / "invalid-discovery.json"
    invalid_path.write_text(json.dumps(artifact))

    result = runner.invoke(app, ["validate-discovery", str(invalid_path), "--db-path", str(db_path)])

    assert result.exit_code == 1
    assert json.loads(result.stdout) == {
        "valid": False,
        "issues": ["success_criteria must not be empty"],
    }


def test_save_discovery_cli_persists_artifact(runner, discovery_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(
        app,
        ["save-discovery", "disc-1", str(discovery_json_path), "--db-path", str(db_path)],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"saved": True, "artifact_id": "disc-1", "version": 1}

    session_factory = create_session_factory(db_path=db_path)
    session = session_factory()
    Base.metadata.create_all(bind=session.get_bind())
    record = session.get(ArtifactRecord, {"artifact_id": "disc-1", "version": 1})

    assert record is not None
    assert record.version == 1
    assert record.readiness_state == "ready"


def test_save_discovery_cli_rejects_out_of_order_version(
    runner,
    discovery_json_path: Path,
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "cli.db"

    result = runner.invoke(
        app,
        ["save-discovery", "disc-1", str(discovery_json_path), "--db-path", str(db_path), "--version", "2"],
    )

    assert result.exit_code != 0
    assert "expected next version 1" in result.stdout


def test_check_discovery_handoff_cli_reports_failure(runner, discovery_json_path: Path, tmp_path: Path) -> None:
    db_path = tmp_path / "cli.db"
    artifact = json.loads(discovery_json_path.read_text())
    artifact["completion_status"]["readiness_state"] = "not_ready"
    artifact["completion_status"]["blocking_gaps"] = ["Need grounded success criteria."]
    invalid_path = tmp_path / "not-ready-discovery.json"
    invalid_path.write_text(json.dumps(artifact))

    result = runner.invoke(app, ["check-discovery-handoff", str(invalid_path), "--db-path", str(db_path)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["accepted"] is False
    assert "completion_status.readiness_state must be 'ready' before Design can begin" in payload["reasons"]


def test_list_skills_cli_includes_discovery(runner) -> None:
    result = runner.invoke(app, ["list-skills"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert any(skill["name"] == "discovery" for skill in payload["skills"])


def test_show_skill_cli_returns_discovery_instructions(runner) -> None:
    result = runner.invoke(app, ["show-skill", "discovery"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["found"] is True
    assert payload["name"] == "discovery"
    assert "discovery.next_turn" in payload["instructions"]
    assert "references/toolchain_workflow.md" in payload["instructions"]


def test_start_discovery_session_cli_returns_skill_context(runner, tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["start-discovery-session", "disc-1", "--db-path", str(tmp_path / "cli.db")],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["artifact_id"] == "disc-1"
    assert payload["skill_name"] == "discovery"
    assert payload["current_artifact"] is None


def test_next_discovery_turn_cli_reviews_skill_authored_turn(
    runner,
    discovery_json_path: Path,
    tmp_path: Path,
) -> None:
    result = runner.invoke(
        app,
        [
            "next-discovery-turn",
            "disc-1",
            "We need measurable success criteria and explicit scope.",
            "--assistant-reply",
            "I tightened the draft around measurable outcomes and explicit scope boundaries.",
            "--artifact-path",
            str(discovery_json_path),
            "--db-path",
            str(tmp_path / "cli.db"),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["session"]["artifact_id"] == "disc-1"
    assert payload["assistant_reply"].startswith("I tightened the draft")
    assert payload["review"]["persistable"] is True


def test_review_discovery_draft_cli_reports_review(
    runner,
    discovery_json_path: Path,
    tmp_path: Path,
) -> None:
    result = runner.invoke(
        app,
        ["review-discovery-draft", str(discovery_json_path), "--db-path", str(tmp_path / "cli.db")],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["persistable"] is True
    assert payload["handoff"]["accepted"] is True


def test_save_discovery_revision_cli_rejects_invalid_candidate(
    runner,
    discovery_json_path: Path,
    tmp_path: Path,
) -> None:
    artifact = json.loads(discovery_json_path.read_text())
    artifact["success_criteria"] = []
    invalid_path = tmp_path / "invalid-discovery-revision.json"
    invalid_path.write_text(json.dumps(artifact))

    result = runner.invoke(
        app,
        ["save-discovery-revision", "disc-1", str(invalid_path), "--db-path", str(tmp_path / "cli.db")],
    )

    assert result.exit_code == 1
    assert "not persistable" in result.stdout


def test_next_discovery_turn_cli_returns_review_and_candidate(
    runner,
    discovery_json_path: Path,
    tmp_path: Path,
) -> None:
    result = runner.invoke(
        app,
        [
            "next-discovery-turn",
            "disc-1",
            "We need explicit scope and measurable outcomes.",
            "--assistant-reply",
            "I tightened the discovery draft and left readiness at ready because the success criteria are explicit.",
            "--artifact-path",
            str(discovery_json_path),
            "--db-path",
            str(tmp_path / "cli.db"),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["assistant_reply"].startswith("I tightened the discovery draft")
    assert payload["review"]["persistable"] is True
    assert payload["candidate_artifact"]["success_criteria"]
    assert payload["session"]["skill_name"] == "discovery"
