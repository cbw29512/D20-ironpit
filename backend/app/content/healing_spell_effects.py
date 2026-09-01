from __future__ import annotations

from app.domain.actions import HealingAction


def _spell_heal(
    spell_id: str, name: str, action_cost: str, range_ft: int,
    dice_count: int, dice_size: int, spellcasting_modifier: int,
) -> HealingAction:
    if spellcasting_modifier < 0:
        raise ValueError(f"Certified {name} requires a nonnegative spellcasting modifier.")
    return HealingAction(
        id=spell_id, name=name, action_cost=action_cost, range_ft=range_ft,
        target_mode="self_or_ally", dice_count=dice_count, dice_size=dice_size,
        healing_bonus=spellcasting_modifier, resource_id="spell-slot-1", resource_cost=1,
        animation="healing",
    )


def build_cure_wounds(spellcasting_modifier: int) -> HealingAction:
    """Printed-level 2024 Cure Wounds; higher-slot casting remains deliberately deferred."""
    return _spell_heal("cure-wounds", "Cure Wounds", "action", 5, 2, 8, spellcasting_modifier)


def build_healing_word(spellcasting_modifier: int) -> HealingAction:
    """Printed-level 2024 Healing Word; higher-slot casting remains deliberately deferred."""
    return _spell_heal("healing-word", "Healing Word", "bonus_action", 60, 2, 4, spellcasting_modifier)
