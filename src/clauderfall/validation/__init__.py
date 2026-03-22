"""Deterministic artifact validation."""

from clauderfall.validation.design import validate_design_artifact
from clauderfall.validation.discovery import validate_discovery_artifact

__all__ = ["validate_discovery_artifact", "validate_design_artifact"]
