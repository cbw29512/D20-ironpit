from __future__ import annotations

from app.domain.spells import SpellAttackAction, SpellModifierEffect, SpellSaveAction


def cantrip_damage_dice(character_level: int) -> int:
    if not 1 <= character_level <= 20:
        raise ValueError("Cantrip scaling requires character level 1-20.")
    return 1 + int(character_level >= 5) + int(character_level >= 11) + int(character_level >= 17)


def build_sacred_flame(save_dc: int, character_level: int) -> SpellSaveAction:
    return SpellSaveAction(
        id="sacred-flame",
        name="Sacred Flame",
        level=0,
        action_cost="action",
        range_ft=60,
        save_ability="dexterity",
        dc=save_dc,
        damage_dice_count=cantrip_damage_dice(character_level),
        damage_dice_size=8,
        damage_type="radiant",
        success_damage="none",
        animation="sacred-flame",
    )


def build_guiding_bolt(attack_bonus: int) -> SpellAttackAction:
    return SpellAttackAction(
        id="guiding-bolt",
        name="Guiding Bolt",
        level=1,
        action_cost="action",
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
