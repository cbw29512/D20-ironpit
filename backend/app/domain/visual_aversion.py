"""Typed fight-local source-scoped visual aversion windows."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisualAversionWindow:
    observer_id: str
    source_combatant_id: str
    expires_on_observer_turn_start: int
