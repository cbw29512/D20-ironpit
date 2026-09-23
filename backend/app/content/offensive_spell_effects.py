from __future__ import annotations

import logging

from app.domain.spells import SpellAttackAction, SpellModifierEffect, SpellSaveAction

logger = logging.getLogger(__name__)


def cantrip_damage_dice(character_level: int) -> int:
    if not 1 <= character_level <= 20:
        raise ValueError("Cantrip scaling requires character level 1-20.")
    return 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)


def build_sacred_flame(save_dc: int, character_level: int, damage_bonus: int = 0) -> SpellSaveAction:
    return SpellSaveAction(
        id="sacred-flame",
        name="Sacred Flame",
        level=0,
        action_cost="action",
        range_ft=60,
        requires_visible_target=True,
        save_ability="dexterity",
        dc=save_dc,
        damage_dice_count=cantrip_damage_dice(character_level),
        damage_dice_size=8,
        damage_bonus=damage_bonus,
        damage_type="radiant",
        success_damage="none",
        animation="sacred-flame",
    )


def build_inflict_wounds(save_dc: int, slot_level: int = 1) -> SpellSaveAction:
    """2024 Inflict Wounds at its printed level or a declared legal upcast slot."""
    try:
        if not 1 <= slot_level <= 9:
            raise ValueError("Inflict Wounds slot level must be between 1 and 9.")
        suffix = "" if slot_level == 1 else f"-l{slot_level}"
        label = "Inflict Wounds" if slot_level == 1 else f"Inflict Wounds ({slot_level}th-Level)"
        return SpellSaveAction(
            id=f"inflict-wounds{suffix}",
            name=label,
            level=slot_level,
            action_cost="action",
            range_ft=5,
            save_ability="constitution",
            dc=save_dc,
            damage_dice_count=2 + (slot_level - 1),
            damage_dice_size=10,
            damage_type="necrotic",
            success_damage="half",
            upcast_dice_per_level=1,
            animation="inflict-wounds",
        )
    except Exception:
        logger.exception("Failed to build Inflict Wounds at slot level %s.", slot_level)
        raise


def build_guiding_bolt(attack_bonus: int) -> SpellAttackAction:
    return SpellAttackAction(
        id="guiding-bolt",
        name="Guiding Bolt",
        level=1,
        action_cost="action",
        attack_kind="ranged",
        range_ft=120,
        attack_bonus=attack_bonus,
        damage_dice_count=4,
        damage_dice_size=6,
        damage_type="radiant",
        on_hit_modifier_effects=[
            SpellModifierEffect(
                kind="attacks-against-advantage",
                consume_on_attack_against=True,
                expires_after_source_turns=1,
            ),
        ],
        animation="guiding-bolt",
        source="SRD 5.2.1 Guiding Bolt",
    )
