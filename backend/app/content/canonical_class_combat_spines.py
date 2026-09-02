from __future__ import annotations

from app.content.barbarian_combat_levels import BARBARIAN_COMBAT_LEVELS
from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.content.druid_combat_levels import DRUID_COMBAT_LEVELS
from app.content.fighter_combat_levels import FIGHTER_COMBAT_LEVELS
from app.content.monk_combat_levels import MONK_COMBAT_LEVELS
from app.content.paladin_combat_levels import PALADIN_COMBAT_LEVELS
from app.content.ranger_combat_levels import RANGER_COMBAT_LEVELS
from app.content.rogue_combat_levels import ROGUE_COMBAT_LEVELS
from app.content.sorcerer_combat_levels import SORCERER_COMBAT_LEVELS
from app.content.warlock_combat_levels import WARLOCK_COMBAT_LEVELS
from app.content.wizard_combat_levels import WIZARD_COMBAT_LEVELS


CANONICAL_CLASS_COMBAT_SPINES: dict[str, dict[int, object]] = {
    "barbarian": BARBARIAN_COMBAT_LEVELS,
    "bard": BARD_COMBAT_LEVELS,
    "cleric": CLERIC_COMBAT_LEVELS,
    "druid": DRUID_COMBAT_LEVELS,
    "fighter": FIGHTER_COMBAT_LEVELS,
    "monk": MONK_COMBAT_LEVELS,
    "paladin": PALADIN_COMBAT_LEVELS,
    "ranger": RANGER_COMBAT_LEVELS,
    "rogue": ROGUE_COMBAT_LEVELS,
    "sorcerer": SORCERER_COMBAT_LEVELS,
    "warlock": WARLOCK_COMBAT_LEVELS,
    "wizard": WIZARD_COMBAT_LEVELS,
}


def canonical_class_combat_spine(class_id: str) -> dict[int, object]:
    try:
        return CANONICAL_CLASS_COMBAT_SPINES[class_id]
    except KeyError as exc:
        raise ValueError(f"Unknown canonical class combat spine: {class_id}.") from exc
