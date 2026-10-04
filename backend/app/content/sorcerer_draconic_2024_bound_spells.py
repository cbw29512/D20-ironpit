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
from app.content.sorcerer_2024_spells import chromatic_orb_2024, dragons_breath_2024, lightning_bolt_2024

logger = logging.getLogger(__name__)


def fire_bonus(level: int, charisma_modifier: int) -> int:
    return charisma_modifier if level >= 6 else 0


def build_nyra_2024_spell_attacks(level: int, attack_bonus: int, charisma_modifier: int):
    try:
        bonus = fire_bonus(level, charisma_modifier)
        attacks = [
            build_fire_bolt_2024(attack_bonus, level, bonus),
            build_poison_spray_2024(attack_bonus, level),
        ]
        if level >= 3:
            attacks.append(chromatic_orb_2024(attack_bonus, bonus))
        return attacks
    except Exception:
        logger.exception("Failed to build 2024 Nyra spell attacks at level %s.", level)
        raise


def build_nyra_2024_spell_saves(level: int, save_dc: int, charisma_modifier: int):
    try:
        bonus = fire_bonus(level, charisma_modifier)
        burning = build_burning_hands_2024(save_dc)
        if bonus:
            burning = burning.model_copy(update={"damage_bonus": bonus})
        actions = [burning, build_thunderwave_2024(save_dc)]
        if level >= 3:
            actions.append(build_shatter_2024(save_dc))
            actions.append(dragons_breath_2024(save_dc))
        if level >= 4:
            actions.append(build_thunderclap_2024(save_dc, level))
        if level >= 5:
            fireball = build_fireball_2024(save_dc)
            if bonus:
                fireball = fireball.model_copy(update={"damage_bonus": bonus})
            actions.append(fireball)
        if level >= 6:
            actions.append(lightning_bolt_2024(save_dc))
        if level >= 7:
            actions.append(build_blight_2024(save_dc))
        if level >= 9:
            actions.append(build_cone_of_cold_2024(save_dc))
        if level >= 11:
            actions.append(build_disintegrate_2024(save_dc))
        if level >= 13:
            actions.append(build_finger_of_death_2024(save_dc))
        if level >= 15:
            actions.append(build_sunburst_2024(save_dc))
        if level >= 17:
            actions.append(build_circle_of_death_2024(save_dc))
        return actions
    except Exception:
        logger.exception("Failed to build 2024 Nyra spell saves at level %s.", level)
        raise
