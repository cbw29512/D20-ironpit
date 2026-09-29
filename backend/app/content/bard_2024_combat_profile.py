from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)

_LYRA_2024_ABILITIES = AbilityScores(
    strength=10,
    dexterity=10,
    constitution=10,
    intelligence=13,
    wisdom=15,
    charisma=17,
)
_LYRA_DAGGER = AttackExpectation(
    weapon_id="dagger",
    ability="dexterity",
    dice_count=1,
    dice_size=4,
    damage_type="piercing",
)


def _skills(level: int) -> tuple[tuple[str, int], ...]:
    if level == 1:
        return (
            ("athletics", 0), ("acrobatics", 2), ("perception", 4),
            ("performance", 5), ("insight", 4), ("religion", 3),
        )
    if level == 2:
        return (
            ("athletics", 1), ("acrobatics", 4), ("perception", 4),
            ("performance", 7), ("insight", 4), ("religion", 3),
        )
    return (
        ("athletics", 2), ("acrobatics", 4), ("perception", 4),
        ("performance", 7), ("insight", 4), ("religion", 3),
        ("deception", 5), ("investigation", 3),
    )


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    spell_slots = {
        1: (("spell-slot-1", 2),),
        2: (("spell-slot-1", 3),),
        3: (("spell-slot-1", 4), ("spell-slot-2", 2)),
    }[level]
    return (
        ("bardic-inspiration", 3),
        *spell_slots,
        ("adrenaline-rush", 2),
        ("relentless-endurance", 1),
    )


def build_lyra_2024_combat_profile(level: int) -> PregenCombatProfile:
    """Independent source-derived combat fingerprint for 2024 Lore Bard levels 1-3."""
    try:
        if level not in {1, 2, 3}:
            raise ValueError("2024 Lyra combat fingerprint currently covers levels 1 through 3.")
        return PregenCombatProfile(
            template_id=f"lyra-silverstring-l{level}",
            archetype="Bard",
            level=level,
            abilities=_LYRA_2024_ABILITIES,
            save_proficiencies=("dexterity", "charisma"),
            armor_class=12,
            max_hp=8 + 5 * (level - 1),
            speed_ft=30,
            skill_bonuses=_skills(level),
            attacks=(_LYRA_DAGGER,),
            weapon_masteries=(),
            resources=_resources(level),
            initiative_bonus=0,
        )
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprint at level %s.", level)
        raise


def build_lyra_2024_combat_profiles() -> tuple[PregenCombatProfile, ...]:
    try:
        return tuple(build_lyra_2024_combat_profile(level) for level in (1, 2, 3))
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprints.")
        raise
