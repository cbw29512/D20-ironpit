from __future__ import annotations

import logging

from app.content.bard_2024_high_damage_spells import build_cone_of_cold_2024, build_sunburst_2024
from app.content.druid_2024_land_spells import (
    build_blight_2024,
    build_burning_hands_2024,
    build_fire_bolt_2024,
)
from app.content.druid_2024_spells import (
    build_faerie_fire_2024,
    build_poison_spray_2024,
    build_starry_wisp_2024,
    build_thunderclap_2024,
    build_thunderwave_2024,
)
from app.content.offensive_spell_effects import build_fireball_2024
from app.domain.spells import SpellAttackAction, SpellSaveAction

logger = logging.getLogger(__name__)


def _with_cantrip_range_bonus(
    action: SpellAttackAction | SpellSaveAction,
    bonus_ft: int,
) -> SpellAttackAction | SpellSaveAction:
    """Apply a source-provided range bonus only to qualifying ranged cantrips."""
    try:
        if bonus_ft <= 0 or action.level != 0 or action.range_ft < 10:
            return action
        return action.model_copy(update={"range_ft": action.range_ft + bonus_ft})
    except Exception:
        logger.exception("Failed to apply cantrip range bonus to %s.", action.id)
        raise


def druid_offensive_actions(
    level: int,
    proficiency_bonus: int,
    wisdom_modifier: int,
) -> tuple[list[SpellAttackAction], list[SpellSaveAction]]:
    """Compile edition-specific Druid spell actions onto shared spell primitives."""
    try:
        save_dc = 8 + proficiency_bonus + wisdom_modifier
        attack_bonus = proficiency_bonus + wisdom_modifier
        damage_bonus = wisdom_modifier if level >= 7 else 0
        range_bonus = 300 if level >= 15 else 0

        attacks = [
            build_poison_spray_2024(attack_bonus, level, damage_bonus),
            *([build_fire_bolt_2024(attack_bonus, level, damage_bonus)] if level >= 3 else []),
            *([build_starry_wisp_2024(attack_bonus, level, damage_bonus)] if level >= 4 else []),
        ]
        saves = [
            *([build_faerie_fire_2024(save_dc)] if level >= 2 else []),
            *([build_burning_hands_2024(save_dc)] if level >= 3 else []),
            *([build_fireball_2024(save_dc)] if level >= 5 else []),
            *([build_blight_2024(save_dc)] if level >= 7 else []),
            *([build_cone_of_cold_2024(save_dc)] if level >= 9 else []),
            *([build_thunderclap_2024(save_dc, level, damage_bonus)] if level >= 10 else []),
            *([build_thunderwave_2024(save_dc)] if level >= 10 else []),
            *([build_sunburst_2024(save_dc)] if level >= 15 else []),
        ]
        return (
            [_with_cantrip_range_bonus(action, range_bonus) for action in attacks],
            [_with_cantrip_range_bonus(action, range_bonus) for action in saves],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Druid offensive actions at level %s.", level)
        raise
