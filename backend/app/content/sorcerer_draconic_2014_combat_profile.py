from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.sorcerer_draconic_2014_data import ability_scores
from app.content.sorcerer_draconic_2014_progression import sorcerer_draconic_2014_level

logger = logging.getLogger(__name__)


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    row = sorcerer_draconic_2014_level(level)
    resources = [
        (f"spell-slot-{spell_level}", uses)
        for spell_level, uses in enumerate(row.spell_slots, start=1) if uses
    ]
    if row.sorcery_points:
        resources.append(("sorcery-points", row.sorcery_points))
    return tuple(resources)


def _skills(level: int) -> tuple[tuple[str, int], ...]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return tuple(sorted({
            "arcana": scores.modifier("intelligence") + pb,
            "medicine": scores.modifier("wisdom") + pb,
            "persuasion": scores.modifier("charisma") + pb,
            "religion": scores.modifier("intelligence") + pb,
        }.items()))
    except Exception:
        logger.exception("Failed to compile Nyra's fingerprint skills at level %s.", level)
        raise


def build_nyra_emberveil_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Nyra combat fingerprint covers levels 1 through 20.")
        scores = ability_scores(level)
        return PregenCombatProfile(
            template_id=f"nyra-emberveil-2014-l{level}",
            archetype="Sorcerer", level=level, abilities=scores,
            save_proficiencies=("constitution", "charisma"),
            armor_class=13 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")) + level,
            speed_ft=30, skill_bonuses=_skills(level),
            attacks=(
                AttackExpectation(
                    "light-crossbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=80, long_range_ft=320,
                ),
            ),
            weapon_masteries=(), resources=_resources(level),
            initiative_bonus=scores.modifier("dexterity"),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Nyra combat fingerprint at level %s.", level)
        raise
