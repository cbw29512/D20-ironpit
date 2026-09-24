from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.warlock_fiend_2014_data import ability_scores
from app.content.warlock_fiend_2014_progression import warlock_fiend_2014_level

logger = logging.getLogger(__name__)


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    row = warlock_fiend_2014_level(level)
    resources = [(f"spell-slot-{row.pact_slot_level}", row.pact_slots)]
    resources.extend((f"mystic-arcanum-{spell_level}", 1) for spell_level in row.mystic_arcanum_levels)
    if level >= 6:
        resources.append(("dark-ones-own-luck", 1))
    return tuple(resources)


def _skills(level: int) -> tuple[tuple[str, int], ...]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return tuple(sorted({
            "arcana": scores.modifier("intelligence") + pb,
            "deception": scores.modifier("charisma") + pb,
            "intimidation": scores.modifier("charisma") + pb,
            "sleight-of-hand": scores.modifier("dexterity") + pb,
        }.items()))
    except Exception:
        logger.exception("Failed to compile Varek's fingerprint skills at level %s.", level)
        raise


def build_varek_ashenmark_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Varek combat fingerprint covers levels 1 through 20.")
        scores = ability_scores(level)
        return PregenCombatProfile(
            template_id=f"varek-ashenmark-2014-l{level}",
            archetype="Warlock", level=level, abilities=scores,
            save_proficiencies=("wisdom", "charisma"),
            armor_class=11 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
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
        logger.exception("Failed to compile 2014 Varek combat fingerprint at level %s.", level)
        raise
