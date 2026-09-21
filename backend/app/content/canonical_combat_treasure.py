from __future__ import annotations

from app.content.pregen_combat_treasure import canonical_treasure_roll, resolve_combat_treasure
from app.content.pregen_treasure_application import apply_combat_treasure_history
from app.domain.combat_treasure import CombatTreasureAward
from app.domain.models import CombatantTemplate


def canonical_combat_treasure_history(
    template: CombatantTemplate,
    class_id: str,
    build_id: str,
    level: int,
) -> list[CombatTreasureAward]:
    """Roll once for every gained level and preserve the resulting item history."""
    if not 1 <= level <= 20:
        raise ValueError("Canonical treasure history requires level 1 through 20.")
    awards: list[CombatTreasureAward] = []
    for gained_level in range(2, level + 1):
        roll = canonical_treasure_roll(template.ruleset, class_id, build_id, gained_level)
        awards.extend(resolve_combat_treasure(template, gained_level, roll))
    return awards


def apply_canonical_combat_treasure(
    template: CombatantTemplate,
    class_id: str,
    build_id: str,
    level: int,
) -> CombatantTemplate:
    return apply_combat_treasure_history(
        template,
        canonical_combat_treasure_history(template, class_id, build_id, level),
    )
