from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def _profile(level: int) -> PregenCombatProfile:
    build = build_aurelia_brightshield_2024_profile(level)
    scores = build.final_ability_scores
    if scores is None:
        raise ValueError("2024 Aurelia combat profile requires final ability scores.")
    pb = proficiency_bonus(level)
    resources = [
        ("lay-on-hands", 5 * level),
        ("spell-slot-1", 4 if level >= 5 else (3 if level >= 3 else 2)),
    ]
    if level >= 2:
        resources.append(("paladins-smite-free-cast", 1))
    if level >= 3:
        resources.append(("channel-divinity", 2))
    if level >= 5:
        resources.extend([
            ("spell-slot-2", 2),
            ("faithful-steed-free-cast", 1),
        ])
    return PregenCombatProfile(
        template_id=build.template_id, archetype="Paladin", level=level,
        abilities=scores, save_proficiencies=("wisdom", "charisma"),
        armor_class=18 + int(level >= 2),
        max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
        speed_ft=30,
        skill_bonuses=(
            ("athletics", scores.modifier("strength") + pb),
            ("intimidation", scores.modifier("charisma") + pb),
            ("insight", scores.modifier("wisdom") + pb),
            ("persuasion", scores.modifier("charisma") + pb),
            ("perception", scores.modifier("wisdom") + pb),
            ("acrobatics", scores.modifier("dexterity") + pb),
            ("medicine", scores.modifier("wisdom") + pb),
            ("religion", scores.modifier("intelligence") + pb),
        ),
        attacks=(
            AttackExpectation(
                "longsword", "strength", 1, 8, "slashing", mastery_property="Sap",
            ),
            AttackExpectation(
                "javelin", "strength", 1, 6, "piercing",
                normal_range_ft=30, long_range_ft=120, mastery_property="Slow",
            ),
        ),
        weapon_masteries=("longsword", "javelin"),
        resources=tuple(resources),
        fighting_style="Defense" if level >= 2 else None,
    )


def build_aurelia_2024_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [_profile(level) for level in range(1, 6)]
    except Exception:
        logger.exception("Failed to build 2024 Aurelia combat fingerprints.")
        raise
