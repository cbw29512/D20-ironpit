from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.sorcerer_2014_progression import sorcerer_2014_level
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile

logger = logging.getLogger(__name__)


def build_nyra_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in (1, 2):
            raise ValueError("2014 Nyra combat fingerprint currently covers levels 1 through 2.")
        profile = build_nyra_emberveil_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        row = sorcerer_2014_level(level)
        resources = tuple(
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        )
        if row.sorcery_points:
            resources = (*resources, ("sorcery-points", row.sorcery_points))
        return PregenCombatProfile(
            template_id=profile.template_id, archetype="Sorcerer", level=level,
            abilities=scores, save_proficiencies=("constitution", "charisma"),
            armor_class=13 + dex,
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")) + level,
            speed_ft=30,
            skill_bonuses=(
                ("arcana", scores.modifier("intelligence") + pb),
                ("persuasion", cha + pb),
                ("perception", scores.modifier("wisdom") + pb),
                ("stealth", dex + pb),
                ("deception", cha + pb),
                ("sleight-of-hand", dex + pb),
            ),
            attacks=(AttackExpectation(
                "light-crossbow", "dexterity", 1, 8, "piercing",
                normal_range_ft=80, long_range_ft=320,
            ),),
            weapon_masteries=(), resources=resources,
            initiative_bonus=dex,
        )
    except Exception:
        logger.exception("Failed to compile Nyra's 2014 combat fingerprint at level %s.", level)
        raise


def build_nyra_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_nyra_2014_combat_profile(level) for level in range(1, 3)]
    except Exception:
        logger.exception("Failed to compile Nyra's 2014 combat fingerprints.")
        raise
