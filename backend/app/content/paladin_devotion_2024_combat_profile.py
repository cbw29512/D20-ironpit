from __future__ import annotations

import logging

from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def build_aurelia_2024_combat_profiles() -> list[PregenCombatProfile]:
    try:
        profile = build_aurelia_brightshield_2024_profile(1)
        scores = profile.final_ability_scores
        if scores is None:
            raise ValueError("2024 Aurelia combat profile requires final ability scores.")
        pb = 2
        return [PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Paladin",
            level=1,
            abilities=scores,
            save_proficiencies=("wisdom", "charisma"),
            armor_class=18,
            max_hp=10 + scores.modifier("constitution"),
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
                AttackExpectation("longsword", "strength", 1, 8, "slashing", mastery_property="Sap"),
                AttackExpectation("javelin", "strength", 1, 6, "piercing", normal_range_ft=30, long_range_ft=120, mastery_property="Slow"),
            ),
            weapon_masteries=("longsword", "javelin"),
            resources=(("lay-on-hands", 5), ("spell-slot-1", 2)),
        )]
    except Exception:
        logger.exception("Failed to build 2024 Aurelia combat fingerprints.")
        raise
