from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.wizard_evoker_2014_data import ability_scores
from app.content.wizard_evoker_2014_progression import wizard_evoker_2014_level

logger = logging.getLogger(__name__)


def build_elian_starweaver_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Elian combat fingerprint covers levels 1 through 20.")
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        resources = tuple(
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(wizard_evoker_2014_level(level).spell_slots, start=1)
            if uses
        )
        return PregenCombatProfile(
            template_id=f"elian-starweaver-2014-l{level}",
            archetype="Wizard",
            level=level,
            abilities=scores,
            save_proficiencies=("intelligence", "wisdom"),
            armor_class=10 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 6, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("arcana", scores.modifier("intelligence") + pb),
                ("history", scores.modifier("intelligence") + pb),
                ("insight", scores.modifier("wisdom") + pb),
                ("investigation", scores.modifier("intelligence") + pb),
            ),
            attacks=(
                AttackExpectation(
                    "light-crossbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=80, long_range_ft=320,
                ),
            ),
            weapon_masteries=(),
            resources=resources,
            initiative_bonus=scores.modifier("dexterity"),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Elian combat fingerprint at level %s.", level)
        raise
