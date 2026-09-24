from __future__ import annotations

import logging

from app.content.bard_lore_2014_data import SPELL_SLOTS, ability_scores, bardic_inspiration_die
from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    try:
        scores = ability_scores(level)
        rows = [("bardic-inspiration", max(1, scores.modifier("charisma")))]
        rows.extend(
            (f"spell-slot-{spell_level}", uses)
            for spell_level, uses in enumerate(SPELL_SLOTS[level], start=1)
        )
        return tuple(rows)
    except Exception:
        logger.exception("Failed to compile 2014 Lyra fingerprint resources at level %s", level)
        raise


def _skills(level: int) -> tuple[tuple[str, int], ...]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        skills = {
            "acrobatics": "dexterity", "deception": "charisma", "history": "intelligence",
            "insight": "wisdom", "perception": "wisdom", "performance": "charisma",
            "persuasion": "charisma",
        }
        if level >= 3:
            skills.update({"arcana": "intelligence", "investigation": "intelligence", "medicine": "wisdom"})
        expertise = {"performance", "persuasion"} if level >= 3 else set()
        if level >= 10:
            expertise.update({"perception", "insight"})
        return tuple(sorted(
            (skill, scores.modifier(ability) + pb * (2 if skill in expertise else 1))
            for skill, ability in skills.items()
        ))
    except Exception:
        logger.exception("Failed to compile 2014 Lyra fingerprint skills at level %s", level)
        raise


def build_lyra_silverstring_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lyra combat fingerprint covers levels 1 through 20.")
        scores = ability_scores(level)
        initiative = scores.modifier("dexterity") + (
            proficiency_bonus(level) // 2 if level >= 2 else 0
        )
        return PregenCombatProfile(
            template_id=f"lyra-silverstring-2014-l{level}",
            archetype="Bard",
            level=level,
            abilities=scores,
            save_proficiencies=("dexterity", "charisma"),
            armor_class=11 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=_skills(level),
            attacks=(
                AttackExpectation("lyra-2014-rapier", "dexterity", 1, 8, "piercing"),
                AttackExpectation(
                    "lyra-2014-dagger", "dexterity", 1, 4, "piercing",
                    normal_range_ft=20, long_range_ft=60,
                ),
            ),
            weapon_masteries=(),
            resources=_resources(level),
            initiative_bonus=initiative,
        )
    except Exception:
        logger.exception("Failed to compile 2014 Lyra combat fingerprint at level %s", level)
        raise
