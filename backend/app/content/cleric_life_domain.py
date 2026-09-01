from __future__ import annotations

from app.domain.actions import ConditionRemovalAction
from app.domain.spells import DefensiveSpellAction


AID = DefensiveSpellAction(
    id="aid",
    name="Aid",
    level=2,
    action_cost="action",
    range_ft=30,
    duration_minutes=480,
    target_policy="friendly",
    target_count=3,
    max_hp_increase=5,
    current_hp_increase=5,
    priority=40,
    animation="aid",
    source="D&D Beyond Basic Rules 2024: Aid",
)


LESSER_RESTORATION = ConditionRemovalAction(
    id="lesser-restoration",
    name="Lesser Restoration",
    action_cost="bonus_action",
    range_ft=5,
    target_mode="self_or_ally",
    removable_conditions=["blinded", "deafened", "paralyzed", "poisoned"],
    max_conditions_per_use=1,
    resource_costs={"spell-slot-2": 1},
    expends_spell_slot=True,
    animation="lesser-restoration",
)


def disciple_of_life_bonus(spell_slot_level: int) -> int:
    if not 1 <= spell_slot_level <= 9:
        raise ValueError("Disciple of Life requires a valid spell-slot level.")
    return 2 + spell_slot_level
