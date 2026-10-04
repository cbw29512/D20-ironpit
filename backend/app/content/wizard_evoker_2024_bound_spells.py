from __future__ import annotations

import logging

from app.content.bard_2024_high_damage_spells import (
    build_circle_of_death_2024,
    build_cone_of_cold_2024,
    build_disintegrate_2024,
    build_finger_of_death_2024,
    build_sunburst_2024,
)
from app.content.bard_2024_spells import build_shatter_2024
from app.content.druid_2024_land_spells import build_blight_2024, build_burning_hands_2024, build_fire_bolt_2024
from app.content.druid_2024_spells import build_poison_spray_2024, build_thunderclap_2024, build_thunderwave_2024
from app.content.offensive_spell_effects import build_fireball_2024
from app.content.sorcerer_2024_spells import lightning_bolt_2024, magic_missile_2024

logger = logging.getLogger(__name__)


def evocation_bonus(level: int, intelligence_modifier: int) -> int:
    return intelligence_modifier if level >= 10 else 0


def _empower(spell, bonus: int):
    return spell.model_copy(update={"damage_bonus": spell.damage_bonus + bonus}) if bonus else spell


def build_elian_2024_spell_attacks(level: int, attack_bonus: int, intelligence_modifier: int):
    try:
        bonus = evocation_bonus(level, intelligence_modifier)
        fire_bolt = build_fire_bolt_2024(attack_bonus, level, bonus)
        poison = build_poison_spray_2024(attack_bonus, level)
        if level >= 3:
            fire_bolt = fire_bolt.model_copy(update={"miss_damage": "half"})
            poison = poison.model_copy(update={"miss_damage": "half"})
        return [fire_bolt, poison]
    except Exception:
        logger.exception("Failed to build 2024 Elian spell attacks at level %s.", level)
        raise


def build_elian_2024_spell_saves(level: int, save_dc: int, intelligence_modifier: int):
    try:
        bonus = evocation_bonus(level, intelligence_modifier)
        thunderclap = build_thunderclap_2024(save_dc, level, bonus)
        if level >= 3:
            thunderclap = thunderclap.model_copy(update={"success_damage": "half"})
        actions = [
            thunderclap,
            _empower(build_burning_hands_2024(save_dc), bonus),
            _empower(build_thunderwave_2024(save_dc), bonus),
        ]
        if level >= 3:
            actions.append(_empower(build_shatter_2024(save_dc), bonus))
        if level >= 5:
            actions.append(_empower(build_fireball_2024(save_dc), bonus))
            actions.append(_empower(lightning_bolt_2024(save_dc), bonus))
        if level >= 7:
            actions.append(build_blight_2024(save_dc))
        if level >= 9:
            actions.append(_empower(build_cone_of_cold_2024(save_dc), bonus))
        if level >= 11:
            actions.append(build_disintegrate_2024(save_dc))
        if level >= 13:
            actions.append(build_finger_of_death_2024(save_dc))
        if level >= 15:
            actions.append(_empower(build_sunburst_2024(save_dc), bonus))
        if level >= 17:
            actions.append(build_circle_of_death_2024(save_dc))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Elian spell saves at level %s.", level)
        raise


def build_elian_2024_auto_hits(level: int, intelligence_modifier: int):
    try:
        missile = magic_missile_2024()
        bonus = evocation_bonus(level, intelligence_modifier)
        return [_empower(missile, bonus)]
    except Exception:
        logger.exception("Failed to build 2024 Elian auto-hit spells at level %s.", level)
        raise
