from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.warlock_2014_progression import warlock_2014_level
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile

logger = logging.getLogger(__name__)


def build_varek_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Varek combat fingerprint currently covers levels 1 through 20.")
        profile = build_varek_ashenmark_2014_profile(level)
        scores = profile.final_ability_scores
        pb = proficiency_bonus(level)
        dex = scores.modifier("dexterity")
        cha = scores.modifier("charisma")
        row = warlock_2014_level(level)
        resources = [(f"spell-slot-{row.pact_slot_level}", row.pact_slots)]
        if level >= 6:
            resources.append(("dark-ones-own-luck", 1))
        for arcanum_level in row.mystic_arcanum_levels:
            resources.append((f"mystic-arcanum-{arcanum_level}", 1))
        if level >= 14:
            resources.append(("hurl-through-hell", 1))
        if level >= 20:
            resources.append(("eldritch-master", 1))
        skills = [
            ("arcana", scores.modifier("intelligence") + pb),
            ("history", scores.modifier("intelligence") + pb),
        ]
        if level >= 18:
            skills.extend((("deception", cha + pb), ("persuasion", cha + pb)))
        return PregenCombatProfile(
            template_id=profile.template_id,
            archetype="Warlock",
            level=level,
            abilities=scores,
            save_proficiencies=("wisdom", "charisma"),
            armor_class=11 + dex,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=tuple(skills),
            attacks=(AttackExpectation(
                "light-crossbow", "dexterity", 1, 8, "piercing",
                normal_range_ft=80, long_range_ft=320,
            ),),
            weapon_masteries=(),
            resources=tuple(resources),
            initiative_bonus=dex,
        )
    except Exception:
        logger.exception("Failed to compile Varek's 2014 combat fingerprint at level %s.", level)
        raise


def build_varek_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_varek_2014_combat_profile(level) for level in range(1, 21)]
    except Exception:
        logger.exception("Failed to compile Varek's 2014 combat fingerprints.")
        raise
