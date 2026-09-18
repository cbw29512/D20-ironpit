from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus
from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)
_SLOTS = {
    1: (), 2: (2,), 3: (3,), 4: (3,), 5: (4, 2),
    6: (4, 2), 7: (4, 3), 8: (4, 3), 9: (4, 3, 2), 10: (4, 3, 2),
}


def _scores(level: int) -> AbilityScores:
    return AbilityScores(
        strength=16 + (2 if level >= 4 else 0),
        dexterity=11,
        constitution=14,
        intelligence=9,
        wisdom=13,
        charisma=15 + (2 if level >= 8 else 0),
    )


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    resources: list[tuple[str, int]] = [("lay-on-hands", 5 * level)]
    resources.extend(
        (f"spell-slot-{spell_level}", uses)
        for spell_level, uses in enumerate(_SLOTS[level], start=1)
    )
    if level >= 3:
        resources.append(("channel-divinity", 1))
    return tuple(resources)


def build_aurelia_brightshield_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Aurelia combat fingerprint covers levels 1 through 10.")
        scores = _scores(level)
        pb = proficiency_bonus(level)
        return PregenCombatProfile(
            template_id=f"aurelia-brightshield-2014-l{level}",
            archetype="Paladin",
            level=level,
            abilities=scores,
            save_proficiencies=("wisdom", "charisma"),
            armor_class=18 + int(level >= 2),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30,
            skill_bonuses=(
                ("athletics", scores.modifier("strength") + pb),
                ("insight", scores.modifier("wisdom") + pb),
                ("history", scores.modifier("intelligence") + pb),
                ("persuasion", scores.modifier("charisma") + pb),
            ),
            attacks=(
                AttackExpectation("longsword", "strength", 1, 8, "slashing"),
                AttackExpectation(
                    "javelin", "strength", 1, 6, "piercing",
                    normal_range_ft=30, long_range_ft=120,
                ),
            ),
            weapon_masteries=(),
            resources=_resources(level),
            fighting_style="Defense" if level >= 2 else None,
            saving_throw_flat_bonus=0,
            condition_immunities=(),
        )
    except Exception:
        logger.exception("Failed to compile Aurelia's 2014 combat fingerprint at level %s", level)
        raise


def build_aurelia_2014_combat_profiles() -> list[PregenCombatProfile]:
    try:
        return [build_aurelia_brightshield_2014_combat_profile(level) for level in range(1, 11)]
    except Exception:
        logger.exception("Failed to compile Aurelia's 2014 combat fingerprint progression")
        raise
