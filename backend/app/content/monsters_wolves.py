from __future__ import annotations

from app.content.capability_registry import build_combatant_from_capabilities
from app.domain.models import CombatantTemplate


def build_wolf() -> CombatantTemplate:
    return build_combatant_from_capabilities("srd-wolf")


def build_dire_wolf() -> CombatantTemplate:
    return build_combatant_from_capabilities("srd-dire-wolf")
