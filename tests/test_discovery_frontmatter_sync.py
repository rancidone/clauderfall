from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path("src/clauderfall/skills/discovery/scripts/sync_frontmatter.py")


def run_script(tmp_path: Path, contents: str, *args: str) -> subprocess.CompletedProcess[str]:
    target = tmp_path / "brief.md"
    target.write_text(contents, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, str(target)],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
    )


def test_sync_rewrites_last_updated_and_sorts_parents(tmp_path: Path) -> None:
    result = run_script(
        tmp_path,
        """---
status: draft
last_updated: 2000-01-01
parents:
- docs/discovery/z.md
- docs/discovery/a.md
- docs/discovery/a.md
---
# Brief
""",
        "--date",
        "2026-04-11",
    )

    assert result.returncode == 0
    rewritten = (tmp_path / "brief.md").read_text(encoding="utf-8")
    assert rewritten == """---
status: draft
last_updated: 2026-04-11
parents:
- docs/discovery/a.md
- docs/discovery/z.md
---
# Brief
"""


def test_sync_omits_empty_parents_list(tmp_path: Path) -> None:
    result = run_script(
        tmp_path,
        """---
status: ready
last_updated: 2000-01-01
parents:
---
Body
""",
        "--date",
        "2026-04-11",
    )

    assert result.returncode == 0
    rewritten = (tmp_path / "brief.md").read_text(encoding="utf-8")
    assert rewritten == """---
status: ready
last_updated: 2026-04-11
---
Body
"""


def test_sync_rejects_unknown_fields(tmp_path: Path) -> None:
    result = run_script(
        tmp_path,
        """---
status: draft
last_updated: 2000-01-01
title: Wrong
---
Body
""",
        "--date",
        "2026-04-11",
    )

    assert result.returncode == 1
    assert "unsupported frontmatter fields" in result.stderr


def test_sync_check_mode_fails_when_rewrite_needed(tmp_path: Path) -> None:
    result = run_script(
        tmp_path,
        """---
status: stable
last_updated: 2000-01-01
---
Body
""",
        "--check",
        "--date",
        "2026-04-11",
    )

    assert result.returncode == 1
    assert (tmp_path / "brief.md").read_text(encoding="utf-8") == """---
status: stable
last_updated: 2000-01-01
---
Body
"""
