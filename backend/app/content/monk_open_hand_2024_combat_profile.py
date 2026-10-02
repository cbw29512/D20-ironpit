from __future__ import annotations

import logging

from app.content.monk_2024_resource_rules import monk_martial_arts_die
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)


def _row(level: int, abilities: AbilityScores, focus_points: int) -> PregenCombatProfile:
    try:
        dexterity = abilities.modifier("dexterity")
        constitution = abilities.modifier("constitution")
        wisdom = abilities.modifier("wisdom")
        proficiency = 5 if level >= 13 else 4 if level >= 9 else 3 if level >= 5 else 2
        return PregenCombatProfile(
            template_id=f"kael-stillwater-l{level}",
            archetype="Monk",
            level=level,
            abilities=abilities,
            save_proficiencies=(
                ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")
                if level >= 14 else ("strength", "dexterity")
            ),
            armor_class=10 + dexterity + wisdom,
            max_hp=(8 + constitution) + (5 + constitution) * (level - 1),
            speed_ft=30 if level == 1 else 55 if level >= 14 else 50 if level >= 10 else 45 if level >= 6 else 40,
            initiative_bonus=dexterity + proficiency,
            skill_bonuses=(
                ("athletics", 1),
                ("acrobatics", dexterity + proficiency),
                ("history", proficiency),
                ("insight", wisdom + proficiency),
                ("nature", proficiency),
                ("perception", wisdom + proficiency),
                ("religion", proficiency),
                ("sleight-of-hand", dexterity + proficiency),
                ("stealth", dexterity + proficiency),
            ),
            attacks=(AttackExpectation("unarmed-strike", "dexterity", 1, monk_martial_arts_die(level), "bludgeoning"),),
            weapon_masteries=(),
            resources=(
                (
                    ("focus-points", focus_points),
                    ("uncanny-metabolism", 1),
                    *((("wholeness-of-body", 1),) if level >= 6 else ()),
                )
                if focus_points else ()
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Kael combat fingerprint at level %s.", level)
        raise


def build_kael_2024_combat_profiles(max_level: int = 16) -> list[PregenCombatProfile]:
    """Return independent combat fingerprints for certified 2024 Kael levels."""
    try:
        if max_level not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}:
            raise ValueError("The current 2024 Kael combat fingerprint covers levels 1-16 only.")
        base = AbilityScores(
            strength=13,
            dexterity=17,
            constitution=15,
            intelligence=10,
            wisdom=10,
            charisma=10,
        )
        level_four = base.model_copy(update={"dexterity": 19})
        level_eight = level_four.model_copy(update={"dexterity": 20, "constitution": 16})
        level_twelve = level_eight.model_copy(update={"wisdom": 12})
        level_sixteen = level_twelve.model_copy(update={"wisdom": 14})
        rows = [_row(1, base, 0)]
        if max_level >= 2:
            rows.append(_row(2, base, 2))
        if max_level >= 3:
            rows.append(_row(3, base, 3))
        if max_level >= 4:
            rows.append(_row(4, level_four, 4))
        if max_level >= 5:
            rows.append(_row(5, level_four, 5))
        if max_level >= 6:
            rows.append(_row(6, level_four, 6))
        if max_level >= 7:
            rows.append(_row(7, level_four, 7))
        if max_level >= 8:
            rows.append(_row(8, level_eight, 8))
        if max_level >= 9:
            rows.append(_row(9, level_eight, 9))
        if max_level >= 10:
            rows.append(_row(10, level_eight, 10))
        if max_level >= 11:
            rows.append(_row(11, level_eight, 11))
        if max_level >= 12:
            rows.append(_row(12, level_twelve, 12))
        if max_level >= 13:
            rows.append(_row(13, level_twelve, 13))
        if max_level >= 14:
            rows.append(_row(14, level_twelve, 14))
        if max_level >= 15:
            rows.append(_row(15, level_twelve, 15))
        if max_level >= 16:
            rows.append(_row(16, level_sixteen, 16))
        return rows
    except Exception:
        logger.exception("Failed to build 2024 Kael combat fingerprints through level %s.", max_level)
        raise
