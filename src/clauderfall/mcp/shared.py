"""Shared helpers for the first Clauderfall MCP adapter surface."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clauderfall.runtime import ArtifactRuntimeResult, OperationStatus, RuntimeServices, build_runtime_services


MCP_RESULT_BY_RUNTIME_STATUS = {
    OperationStatus.OK: "success",
    OperationStatus.WARNING: "warning",
    OperationStatus.ERROR: "failure",
}


class MCPValidationError(ValueError):
    """Raised when MCP input validation fails before runtime invocation."""


@dataclass(frozen=True)
class MCPToolSpec:
    """Thin local representation of one registered MCP tool."""

    name: str
    description: str
    input_schema: dict[str, Any]


def build_services_for_repo_root(repo_root: str | Path, docs_root: str | Path | None = None) -> RuntimeServices:
    """Bootstrap runtime services from the requested repo and docs roots."""

    resolved_repo_root = Path(repo_root)
    resolved_docs_root = resolve_docs_root(
        repo_root=resolved_repo_root,
        docs_root=docs_root,
    )
    return build_runtime_services(resolved_docs_root, repo_root=resolved_repo_root)


def resolve_docs_root(*, repo_root: Path, docs_root: str | Path | None) -> Path:
    """Resolve the effective docs root from repo root and an optional override."""

    candidate = Path("docs") if docs_root is None else Path(docs_root)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return candidate.resolve()


def map_runtime_result(result: ArtifactRuntimeResult) -> dict[str, Any]:
    """Map the shared runtime result envelope into the published MCP shape."""

    mapped: dict[str, Any] = {
        "result": MCP_RESULT_BY_RUNTIME_STATUS[result.result.status],
    }

    artifacts = {
        name: _serialize_value(value)
        for name, value in result.artifacts.items()
    }
    metadata = {
        name: _serialize_value(value)
        for name, value in result.metadata.items()
    }
    warnings = list(result.warnings)
    if result.result.warnings:
        warnings.extend(result.result.warnings)
    if warnings:
        mapped["warnings"] = warnings
    if artifacts:
        mapped["artifacts"] = artifacts
    if metadata:
        mapped["metadata"] = metadata
    return mapped


def validation_failure(*, code: str, message: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the shared MCP failure shape for boundary validation errors."""

    return {
        "result": "failure",
        "warnings": [code],
        "artifacts": {},
        "metadata": {"message": message, **(metadata or {})},
    }



def require_string(payload: dict[str, Any], field: str) -> str:
    """Require a non-empty string field from the tool payload."""

    value = payload.get(field)
    if not isinstance(value, str) or not value:
        raise MCPValidationError(f"{field} is required and must be a non-empty string")
    return value


def optional_string(payload: dict[str, Any], field: str) -> str | None:
    """Accept an optional string field from the tool payload."""

    value = payload.get(field)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise MCPValidationError(f"{field} must be a non-empty string when present")
    return value


def optional_bool(payload: dict[str, Any], field: str, *, default: bool = False) -> bool:
    """Accept an optional boolean field from the tool payload."""

    value = payload.get(field, default)
    if not isinstance(value, bool):
        raise MCPValidationError(f"{field} must be a boolean")
    return value


def require_object(payload: dict[str, Any], field: str) -> dict[str, Any]:
    """Require a JSON-object-like mapping from the tool payload."""

    value = payload.get(field)
    if not isinstance(value, dict):
        if isinstance(value, str):
            raise MCPValidationError(
                f"{field} is required and must be an object; got string. "
                f"Do not JSON-encode {field}."
            )
        raise MCPValidationError(f"{field} is required and must be an object")
    return value


def require_string_list(payload: dict[str, Any], field: str) -> list[str]:
    """Require a non-empty list of non-empty strings from the tool payload."""

    value = payload.get(field)
    if not isinstance(value, list) or not value:
        raise MCPValidationError(f"{field} is required and must be a non-empty array of strings")
    if not all(isinstance(item, str) and item for item in value):
        raise MCPValidationError(f"{field} must contain only non-empty strings")
    return value


def _serialize_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value
