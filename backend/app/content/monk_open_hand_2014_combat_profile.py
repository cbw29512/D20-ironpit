from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile

logger = logging.getLogger(__name__)


def _martial_arts_die(level: int) -> int:
    return 4 if level < 5 else 6


def _speed(level: int) -> int:
    if level >= 10:
        return 50
    if level >= 6:
        return 45
    if level >= 2:
        return 40
    return 30


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    resources: list[tuple[str, int]] = []
    if level >= 2:
        resources.append(("ki", level))
    if level >= 6:
        resources.append(("wholeness-of-body", 1))
    return tuple(resources)


def build_kael_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        source = build_kael_stillwater_2014_profile(level)
        scores = source.final_ability_scores
        pb = proficiency_bonus(level)
        dexterity = scores.modifier("dexterity")
        wisdom = scores.modifier("wisdom")
        martial_die = _martial_arts_die(level)
        return PregenCombatProfile(
            template_id=source.template_id,
            archetype="Monk",
            level=level,
            abilities=scores,
            save_proficiencies=("strength", "dexterity"),
            armor_class=10 + dexterity + wisdom,
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=_speed(level),
            skill_bonuses=(
                ("acrobatics", dexterity + pb),
                ("stealth", dexterity + pb),
                ("insight", wisdom + pb),
                ("religion", scores.modifier("intelligence") + pb),
            ),
            attacks=(
                AttackExpectation(
                    "unarmed-strike",
                    "dexterity",
                    1,
                    martial_die,
                    "bludgeoning",
                ),
                AttackExpectation(
                    "shortsword",
                    "dexterity",
                    1,
                    6,
                    "piercing",
                ),
            ),
            weapon_masteries=(),
            resources=_resources(level),
            initiative_bonus=dexterity,
            condition_immunities=("poisoned",) if level >= 10 else (),
        )
    except Exception:
        logger.exception("Failed 2014 Kael combat profile at level %s", level)
        raise


def build_kael_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_kael_2014_combat_profile(level) for level in range(1, 11)]
    except Exception:
        logger.exception("Failed to compile 2014 Kael combat fingerprints")
        raise
