from __future__ import annotations

from app.domain.actions import HealingAction


def build_cure_wounds(spellcasting_modifier: int) -> HealingAction:
    """Build printed-level 2024 Cure Wounds; higher-slot casting remains deliberately deferred."""
    if spellcasting_modifier < 0:
        raise ValueError("Certified Cure Wounds requires a nonnegative spellcasting modifier.")
    return HealingAction(
        id="cure-wounds",
        name="Cure Wounds",
        action_cost="action",
        range_ft=5,
        target_mode="self_or_ally",
        dice_count=2,
        dice_size=8,
        healing_bonus=spellcasting_modifier,
        resource_id="spell-slot-1",
        resource_cost=1,
        animation="healing",
    )
