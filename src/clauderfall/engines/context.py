"""Context engine orchestration entry points."""

from __future__ import annotations

from clauderfall.artifacts.context import ContextPacket
from clauderfall.validation.context import validate_context_packet


class ContextEngine:
    """Thin orchestration wrapper for the Context vertical slice."""

    def validate(self, packet: ContextPacket) -> list[str]:
        return validate_context_packet(packet)
