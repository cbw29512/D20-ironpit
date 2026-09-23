from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.level_resources import cleric_2014_channel_divinity_uses
from app.content.spell_slot_progression import spell_slot_resources
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def build_seraphine_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 4):
            raise ValueError("2014 Seraphine combat fingerprint is currently certified through level 3.")
        source = build_seraphine_dawnshield_2014_profile(level)
        scores = source.final_ability_scores
        pb = proficiency_bonus(level)
        wisdom = scores.modifier("wisdom")
        return PregenCombatProfile(
            template_id=source.template_id,
            archetype="Cleric",
            level=level,
            abilities=scores,
            save_proficiencies=("wisdom", "charisma"),
            armor_class=16,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")) + level,
            speed_ft=25,
            skill_bonuses=(
                ("insight", wisdom + pb),
                ("religion", scores.modifier("intelligence") + pb),
                ("medicine", wisdom + pb),
                ("persuasion", scores.modifier("charisma") + pb),
            ),
            attacks=(
                AttackExpectation("warhammer", "strength", 1, 8, "bludgeoning"),
                AttackExpectation(
                    "light-crossbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=80, long_range_ft=320,
                ),
            ),
            weapon_masteries=(),
            resources=tuple([
                *spell_slot_resources("cleric", level).items(),
                *((("channel-divinity", cleric_2014_channel_divinity_uses(level)),)
                  if cleric_2014_channel_divinity_uses(level) else ()),
            ]),
            damage_resistances=("poison",),
        )
    except Exception:
        logger.exception("Failed to compile Seraphine's 2014 combat fingerprint at level %s.", level)
        raise


def build_seraphine_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_seraphine_2014_combat_profile(level) for level in range(1, 4)]
    except Exception:
        logger.exception("Failed to compile Seraphine's 2014 combat fingerprints.")
        raise
