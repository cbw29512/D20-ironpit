from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.warlock_combat_levels import WARLOCK_COMBAT_LEVELS
from app.content.warlock_fiend_2024_profile import build_varek_ashenmark_2024_profile

logger = logging.getLogger(__name__)


def build_varek_2024_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2024 Varek combat fingerprint currently covers levels 1 through 20.")
        profile = build_varek_ashenmark_2024_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        intel = scores.modifier("intelligence")
        wis = scores.modifier("wisdom")
        row = WARLOCK_COMBAT_LEVELS[level]
        resources = [(f"spell-slot-{row.pact_slot_level}", row.pact_slots)]
        if level >= 2:
            resources.append(("magical-cunning", 1))
        if level >= 6:
            resources.append(("dark-ones-own-luck", max(1, cha)))
        for arcanum_level, unlock in ((6, 11), (7, 13), (8, 15), (9, 17)):
            if level >= unlock:
                resources.append((f"mystic-arcanum-{arcanum_level}", 1))
        if level >= 14:
            resources.append(("hurl-through-hell", 1))
        if level >= 19:
            resources.append(("boon-of-fate", 1))
        return PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Warlock",
            level=level,
            abilities=scores,
            save_proficiencies=("wisdom", "charisma"),
            armor_class=11 + dex,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("arcana", intel + pb),
                ("history", intel + pb),
                ("insight", wis + pb),
                ("religion", intel + pb),
                ("deception", cha + pb),
                ("persuasion", cha + pb),
                ("investigation", intel + pb),
                ("intimidation", cha + pb),
            ),
            attacks=(AttackExpectation(
                "dagger", "dexterity", 1, 4, "piercing",
            ),),
            weapon_masteries=(),
            resources=tuple(resources),
            initiative_bonus=dex,
        )
    except Exception:
        logger.exception("Failed to compile Varek's 2024 combat fingerprint at level %s.", level)
        raise


def build_varek_2024_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_varek_2024_combat_profile(level) for level in range(1, 21)]
    except Exception:
        logger.exception("Failed to compile Varek's 2024 combat fingerprints.")
        raise
