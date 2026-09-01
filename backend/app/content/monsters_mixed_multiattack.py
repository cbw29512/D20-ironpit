from __future__ import annotations

from app.content.capability_registry import build_combatant_from_capabilities
from app.domain.models import CombatantTemplate


def build_giant_constrictor_snake() -> CombatantTemplate:
    return build_combatant_from_capabilities("srd-giant-constrictor-snake")
