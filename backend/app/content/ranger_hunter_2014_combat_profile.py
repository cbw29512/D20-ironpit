from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.ranger_hunter_2014_data import ability_scores
from app.content.ranger_hunter_2014_progression import ranger_hunter_2014_level

logger = logging.getLogger(__name__)


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    row = ranger_hunter_2014_level(level)
    return tuple(
        (f"spell-slot-{spell_level}", uses)
        for spell_level, uses in enumerate(row.spell_slots, start=1)
        if uses
    )


def _skills(level: int) -> tuple[tuple[str, int], ...]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return tuple(sorted({
            "athletics": scores.modifier("strength") + pb,
            "investigation": scores.modifier("intelligence") + pb,
            "perception": scores.modifier("wisdom") + pb,
            "stealth": scores.modifier("dexterity") + pb,
            "survival": scores.modifier("wisdom") + pb,
        }.items()))
    except Exception:
        logger.exception("Failed to compile Rowan's fingerprint skills at level %s.", level)
        raise


def build_rowan_ashtrail_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Rowan combat fingerprint covers levels 1 through 20.")
        scores = ability_scores(level)
        return PregenCombatProfile(
            template_id=f"rowan-ashtrail-2014-l{level}",
            archetype="Ranger", level=level, abilities=scores,
            save_proficiencies=("strength", "dexterity"),
            armor_class=16,
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30, skill_bonuses=_skills(level),
            attacks=(
                AttackExpectation(
                    "longbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=150, long_range_ft=600,
                    style_attack_bonus=2 if level >= 2 else 0,
                ),
                AttackExpectation("shortsword", "dexterity", 1, 6, "piercing"),
            ),
            weapon_masteries=(), resources=_resources(level),
            fighting_style="Archery" if level >= 2 else None,
            initiative_bonus=scores.modifier("dexterity"),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rowan combat fingerprint at level %s.", level)
        raise
