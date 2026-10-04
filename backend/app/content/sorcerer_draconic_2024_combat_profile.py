from __future__ import annotations

import logging

from app.content.character_math import proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.sorcerer_combat_levels import SORCERER_COMBAT_LEVELS
from app.content.sorcerer_draconic_2024_math import nyra_2024_armor_class, nyra_2024_hit_points
from app.content.sorcerer_draconic_2024_profile import build_nyra_emberveil_2024_profile

logger = logging.getLogger(__name__)


def build_nyra_2024_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Nyra combat fingerprint currently covers levels 1 through 20.")
        profile = build_nyra_emberveil_2024_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        intel = scores.modifier("intelligence")
        wis = scores.modifier("wisdom")
        row = SORCERER_COMBAT_LEVELS[level]
        resources = [
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
        resources.append(("innate-sorcery", 2))
        if level >= 2:
            resources.append(("sorcery-points", row.sorcery_points))
        if level >= 14:
            resources.append(("dragon-wings", 1))
        if level >= 19:
            resources.append(("boon-of-fate", 1))
        return PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Sorcerer",
            level=level,
            abilities=scores,
            save_proficiencies=("constitution", "charisma"),
            armor_class=nyra_2024_armor_class(level, dex, cha),
            max_hp=nyra_2024_hit_points(level, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("arcana", intel + pb),
                ("persuasion", cha + pb),
                ("insight", wis + pb),
                ("religion", intel + pb),
                ("deception", cha + pb),
                ("intimidation", cha + pb),
                ("investigation", intel + pb),
                ("history", intel + pb),
            ),
            attacks=(AttackExpectation("dagger", "dexterity", 1, 4, "piercing"),),
            weapon_masteries=(),
            resources=tuple(resources),
            damage_resistances=("fire",) if level >= 6 else (),
            initiative_bonus=dex,
        )
    except Exception:
        logger.exception("Failed to compile Nyra's 2024 combat fingerprint at level %s.", level)
        raise


def build_nyra_2024_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_nyra_2024_combat_profile(level) for level in range(1, 21)]
    except Exception:
        logger.exception("Failed to compile Nyra's 2024 combat fingerprints.")
        raise
