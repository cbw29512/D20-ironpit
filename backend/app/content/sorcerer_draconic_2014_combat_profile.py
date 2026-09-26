from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile

logger = logging.getLogger(__name__)


def build_nyra_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level != 1:
            raise ValueError("2014 Nyra combat fingerprint currently covers level 1.")
        profile = build_nyra_emberveil_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        return PregenCombatProfile(
            template_id=profile.template_id, archetype="Sorcerer", level=1,
            abilities=scores, save_proficiencies=("constitution", "charisma"),
            armor_class=13 + dex, max_hp=7, speed_ft=30,
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
            weapon_masteries=(), resources=(("spell-slot-1", 2),),
            initiative_bonus=dex,
        )
    except Exception:
        logger.exception("Failed to compile Nyra's 2014 combat fingerprint at level %s.", level)
        raise


def build_nyra_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_nyra_2014_combat_profile(1)]
    except Exception:
        logger.exception("Failed to compile Nyra's 2014 combat fingerprints.")
        raise
