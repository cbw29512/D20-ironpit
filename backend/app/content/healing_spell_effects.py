from __future__ import annotations

import logging

from app.domain.actions import HealingAction

logger = logging.getLogger(__name__)


def _spell_heal(
    spell_id: str, name: str, action_cost: str, range_ft: int,
    dice_count: int, dice_size: int, spellcasting_modifier: int, extra_healing_bonus: int = 0,
) -> HealingAction:
    if spellcasting_modifier < 0 or extra_healing_bonus < 0:
        raise ValueError(f"Certified {name} requires nonnegative healing modifiers.")
    return HealingAction(
        id=spell_id, name=name, action_cost=action_cost, range_ft=range_ft,
        target_mode="self_or_ally", dice_count=dice_count, dice_size=dice_size,
        healing_bonus=spellcasting_modifier + extra_healing_bonus,
        resource_id="spell-slot-1", resource_cost=1, animation="healing",
    )


def build_cure_wounds(spellcasting_modifier: int, extra_healing_bonus: int = 0) -> HealingAction:
    """Printed-level 2024 Cure Wounds; higher-slot casting remains deliberately deferred."""
    return _spell_heal(
        "cure-wounds", "Cure Wounds", "action", 5, 2, 8,
        spellcasting_modifier, extra_healing_bonus,
    )


def build_healing_word(spellcasting_modifier: int, extra_healing_bonus: int = 0) -> HealingAction:
    """Printed-level 2024 Healing Word; higher-slot casting remains deliberately deferred."""
    return _spell_heal(
        "healing-word", "Healing Word", "bonus_action", 60, 2, 4,
        spellcasting_modifier, extra_healing_bonus,
    )


def build_mass_healing_word(
    spellcasting_modifier: int,
    extra_healing_bonus: int = 0,
) -> HealingAction:
    """Printed-level 2024 Mass Healing Word as a shared multi-target healing action."""
    if spellcasting_modifier < 0 or extra_healing_bonus < 0:
        raise ValueError("Certified Mass Healing Word requires nonnegative healing modifiers.")
    return HealingAction(
        id="mass-healing-word",
        name="Mass Healing Word",
        action_cost="bonus_action",
        range_ft=60,
        target_mode="self_or_ally",
        max_targets=6,
        dice_count=2,
        dice_size=4,
        healing_bonus=spellcasting_modifier + extra_healing_bonus,
        resource_id="spell-slot-3",
        resource_cost=1,
        animation="healing",
    )


def build_mass_cure_wounds(
    spellcasting_modifier: int,
    extra_healing_bonus: int = 0,
    slot_level: int = 5,
) -> HealingAction:
    """2024 Mass Cure Wounds at its printed level or a declared legal upcast slot."""
    try:
        if spellcasting_modifier < 0 or extra_healing_bonus < 0:
            raise ValueError("Certified Mass Cure Wounds requires nonnegative healing modifiers.")
        if not 5 <= slot_level <= 9:
            raise ValueError("Mass Cure Wounds slot level must be between 5 and 9.")
        suffix = "" if slot_level == 5 else f"-l{slot_level}"
        label = "Mass Cure Wounds" if slot_level == 5 else f"Mass Cure Wounds ({slot_level}th-Level)"
        return HealingAction(
            id=f"mass-cure-wounds{suffix}",
            name=label,
            action_cost="action",
            range_ft=60,
            target_mode="self_or_ally",
            max_targets=6,
            dice_count=5 + (slot_level - 5),
            dice_size=8,
            healing_bonus=spellcasting_modifier + extra_healing_bonus,
            resource_id=f"spell-slot-{slot_level}",
            resource_cost=1,
            animation="healing",
        )
    except Exception:
        logger.exception("Failed to build Mass Cure Wounds at slot level %s.", slot_level)
        raise
