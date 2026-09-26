from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.ranger_2014_progression import ranger_2014_level
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile

logger = logging.getLogger(__name__)


def build_rowan_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 14):
            raise ValueError("2014 Rowan combat fingerprint currently covers levels 1 through 13.")
        profile = build_rowan_ashtrail_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        resources = tuple(
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(ranger_2014_level(level).spell_slots, start=1)
            if uses
        )
        return PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Ranger",
            level=level,
            abilities=scores,
            save_proficiencies=("strength", "dexterity"),
            armor_class=11 + dexterity,
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=35,
            skill_bonuses=(
                ("athletics", scores.modifier("strength") + pb),
                ("survival", wisdom + pb),
                ("perception", wisdom + pb),
                ("stealth", dexterity + pb),
                ("insight", wisdom + pb),
                ("investigation", scores.modifier("intelligence") + pb),
            ),
            attacks=(
                AttackExpectation(
                    "longbow", "dexterity", 1, 8, "piercing",
                    normal_range_ft=150, long_range_ft=600,
                    style_attack_bonus=2 if level >= 2 else 0,
                ),
                AttackExpectation("shortsword", "dexterity", 1, 6, "piercing"),
            ),
            weapon_masteries=(),
            resources=resources,
            fighting_style="Archery" if level >= 2 else None,
        )
    except Exception:
        logger.exception("Failed to compile Rowan's 2014 combat fingerprint at level %s.", level)
        raise


def build_rowan_2014_combat_profiles() -> list[PregenCombatProfile]:
    return [build_rowan_2014_combat_profile(level) for level in range(1, 14)]
