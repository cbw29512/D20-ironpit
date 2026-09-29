from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)

_LYRA_2024_BASE_ABILITIES = AbilityScores(
    strength=10,
    dexterity=10,
    constitution=10,
    intelligence=13,
    wisdom=15,
    charisma=17,
)


def _abilities(level: int) -> AbilityScores:
    if level >= 16:
        return _LYRA_2024_BASE_ABILITIES.model_copy(update={"wisdom": 20, "charisma": 20})
    if level >= 12:
        return _LYRA_2024_BASE_ABILITIES.model_copy(update={"wisdom": 18, "charisma": 20})
    if level >= 8:
        return _LYRA_2024_BASE_ABILITIES.model_copy(update={"wisdom": 16, "charisma": 20})
    if level >= 4:
        return _LYRA_2024_BASE_ABILITIES.model_copy(update={"charisma": 19})
    return _LYRA_2024_BASE_ABILITIES
_LYRA_DAGGER = AttackExpectation(
    weapon_id="dagger",
    ability="dexterity",
    dice_count=1,
    dice_size=4,
    damage_type="piercing",
)


def build_lyra_2024_combat_profile(level: int) -> PregenCombatProfile:
    """Independent source-derived combat fingerprint for the certified Bard progression."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}:
            raise ValueError("2024 Lyra combat fingerprint currently covers levels 1 through 16.")
        proficiency_bonus = 2 + ((level - 1) // 4)
        acrobatics = 0 + (proficiency_bonus * (2 if level >= 2 else 1))
        abilities = _abilities(level)
        charisma_modifier = abilities.modifier("charisma")
        max_hp = {1: 8, 2: 13, 3: 18, 4: 23, 5: 28, 6: 33, 7: 38, 8: 43, 9: 48, 10: 53, 11: 58, 12: 63, 13: 68, 14: 73, 15: 78, 16: 83}[level]
        slot_rows = {
            1: (("spell-slot-1", 2),),
            2: (("spell-slot-1", 3),),
            3: (("spell-slot-1", 4), ("spell-slot-2", 2)),
            4: (("spell-slot-1", 4), ("spell-slot-2", 3)),
            5: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 2)),
            6: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3)),
            7: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 1)),
            8: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 2)),
            9: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 1)),
            10: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 2)),
            11: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1)),
            12: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1)),
            13: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1), ("spell-slot-7", 1)),
            14: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1), ("spell-slot-7", 1)),
            15: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1), ("spell-slot-7", 1), ("spell-slot-8", 1)),
            16: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 3), ("spell-slot-5", 2), ("spell-slot-6", 1), ("spell-slot-7", 1), ("spell-slot-8", 1)),
        }
        wisdom_modifier = abilities.modifier("wisdom")
        return PregenCombatProfile(
            template_id=f"lyra-silverstring-l{level}",
            archetype="Bard",
            level=level,
            abilities=abilities,
            save_proficiencies=("dexterity", "charisma"),
            armor_class=12,
            max_hp=max_hp,
            speed_ft=30,
            skill_bonuses=(
                ("athletics", 0),
                ("acrobatics", acrobatics),
                ("perception", wisdom_modifier + proficiency_bonus * (2 if level >= 9 else 1)),
                ("performance", charisma_modifier + proficiency_bonus * (2 if level >= 9 else 1)),
                ("insight", wisdom_modifier + proficiency_bonus),
                ("religion", 1 + proficiency_bonus),
            ),
            attacks=(_LYRA_DAGGER,),
            weapon_masteries=(),
            resources=(
                ("bardic-inspiration", charisma_modifier),
                *slot_rows[level],
                ("adrenaline-rush", proficiency_bonus),
                ("relentless-endurance", 1),
            ),
            initiative_bonus=0,
        )
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprint at level %s.", level)
        raise


def build_lyra_2024_combat_profiles() -> tuple[PregenCombatProfile, ...]:
    try:
        return tuple(build_lyra_2024_combat_profile(level) for level in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16))
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprints.")
        raise
