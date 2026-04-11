#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ALLOWED_STATUS = {"draft", "ready", "stable"}
ALLOWED_FIELDS = ("status", "last_updated", "parents")


class FrontmatterError(ValueError):
    """Raised when a discovery brief has invalid frontmatter."""


@dataclass(frozen=True)
class FrontmatterDocument:
    frontmatter: dict[str, object]
    body: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize discovery brief frontmatter after a write.",
    )
    parser.add_argument("paths", nargs="+", help="Markdown file(s) to normalize.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate without rewriting files.",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Override last_updated for deterministic tests.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed = False

    try:
        for raw_path in args.paths:
            path = Path(raw_path)
            updated = normalize_file(path, today=args.date, check=args.check)
            changed = changed or updated
    except FrontmatterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.check and changed:
        return 1

    return 0


def normalize_file(path: Path, *, today: str, check: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    parsed = parse_document(path, original)
    normalized_frontmatter = normalize_frontmatter(path, parsed.frontmatter, today=today)
    normalized = render_document(normalized_frontmatter, parsed.body)

    if normalized == original:
        return False

    if not check:
        path.write_text(normalized, encoding="utf-8")

    return True


def parse_document(path: Path, contents: str) -> FrontmatterDocument:
    if not contents.startswith("---\n"):
        raise FrontmatterError(f"{path}: missing opening frontmatter delimiter")

    closing = contents.find("\n---\n", 4)
    if closing == -1:
        raise FrontmatterError(f"{path}: missing closing frontmatter delimiter")

    raw_frontmatter = contents[4:closing]
    body = contents[closing + len("\n---\n") :]
    frontmatter = parse_frontmatter(path, raw_frontmatter)
    return FrontmatterDocument(frontmatter=frontmatter, body=body)


def parse_frontmatter(path: Path, raw_frontmatter: str) -> dict[str, object]:
    frontmatter: dict[str, object] = {}
    current_key: str | None = None

    for lineno, line in enumerate(raw_frontmatter.splitlines(), start=2):
        if not line.strip():
            continue

        if line.startswith("- "):
            if current_key is None:
                raise FrontmatterError(f"{path}:{lineno}: list item without a key")
            value = line[2:].strip()
            if not value:
                raise FrontmatterError(f"{path}:{lineno}: empty list item")
            frontmatter.setdefault(current_key, [])
            current_value = frontmatter[current_key]
            if not isinstance(current_value, list):
                raise FrontmatterError(f"{path}:{lineno}: mixed scalar and list values")
            current_value.append(value)
            continue

        if ":" not in line:
            raise FrontmatterError(f"{path}:{lineno}: invalid frontmatter line")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            raise FrontmatterError(f"{path}:{lineno}: empty frontmatter key")
        if key in frontmatter:
            raise FrontmatterError(f"{path}:{lineno}: duplicate key `{key}`")

        if value:
            frontmatter[key] = value
            current_key = None
        else:
            frontmatter[key] = []
            current_key = key

    return frontmatter


def normalize_frontmatter(
    path: Path,
    frontmatter: dict[str, object],
    *,
    today: str,
) -> dict[str, object]:
    unknown = sorted(key for key in frontmatter if key not in ALLOWED_FIELDS)
    if unknown:
        raise FrontmatterError(
            f"{path}: unsupported frontmatter fields: {', '.join(unknown)}"
        )

    status = frontmatter.get("status")
    if not isinstance(status, str) or status not in ALLOWED_STATUS:
        allowed = ", ".join(sorted(ALLOWED_STATUS))
        raise FrontmatterError(f"{path}: `status` must be one of {allowed}")

    parents = frontmatter.get("parents", [])
    if isinstance(parents, str):
        raise FrontmatterError(f"{path}: `parents` must be a list when present")
    if not isinstance(parents, list):
        raise FrontmatterError(f"{path}: `parents` must be a list when present")
    normalized_parents = sorted(dict.fromkeys(parent.strip() for parent in parents if parent.strip()))

    normalized: dict[str, object] = {
        "status": status,
        "last_updated": today,
    }
    if normalized_parents:
        normalized["parents"] = normalized_parents

    return normalized


def render_document(frontmatter: dict[str, object], body: str) -> str:
    lines = ["---"]
    for field in ALLOWED_FIELDS:
        if field not in frontmatter:
            continue
        value = frontmatter[field]
        if isinstance(value, list):
            lines.append(f"{field}:")
            lines.extend(f"- {item}" for item in value)
        else:
            lines.append(f"{field}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


if __name__ == "__main__":
    raise SystemExit(main())
