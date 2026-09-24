from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.druid_land_2014_data import ability_scores
from app.content.druid_land_2014_progression import druid_land_2014_level
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def build_thalen_greenbough_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Thalen combat fingerprint covers levels 1 through 20.")
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        resources = tuple(
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(druid_land_2014_level(level).spell_slots, start=1)
            if uses
        )
        return PregenCombatProfile(
            template_id=f"thalen-greenbough-2014-l{level}",
            archetype="Druid",
            level=level,
            abilities=scores,
            save_proficiencies=("intelligence", "wisdom"),
            armor_class=13 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("arcana", scores.modifier("intelligence") + pb),
                ("medicine", scores.modifier("wisdom") + pb),
                ("nature", scores.modifier("intelligence") + pb),
                ("perception", scores.modifier("wisdom") + pb),
            ),
            attacks=(AttackExpectation("scimitar", "dexterity", 1, 6, "slashing"),),
            weapon_masteries=(),
            resources=resources,
            initiative_bonus=scores.modifier("dexterity"),
        )
    except Exception:
        logger.exception("Failed to compile 2014 Thalen combat fingerprint at level %s.", level)
        raise
