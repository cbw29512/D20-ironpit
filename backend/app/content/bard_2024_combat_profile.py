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
    return (
        _LYRA_2024_BASE_ABILITIES.model_copy(update={"charisma": 19})
        if level >= 4 else _LYRA_2024_BASE_ABILITIES
    )
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
        if level not in {1, 2, 3, 4, 5, 6, 7}:
            raise ValueError("2024 Lyra combat fingerprint currently covers levels 1 through 7.")
        acrobatics = 2 if level == 1 else (4 if level <= 4 else 6)
        abilities = _abilities(level)
        charisma_modifier = abilities.modifier("charisma")
        max_hp = {1: 8, 2: 13, 3: 18, 4: 23, 5: 28, 6: 33, 7: 38}[level]
        slot_rows = {
            1: (("spell-slot-1", 2),),
            2: (("spell-slot-1", 3),),
            3: (("spell-slot-1", 4), ("spell-slot-2", 2)),
            4: (("spell-slot-1", 4), ("spell-slot-2", 3)),
            5: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 2)),
            6: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3)),
            7: (("spell-slot-1", 4), ("spell-slot-2", 3), ("spell-slot-3", 3), ("spell-slot-4", 1)),
        }
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
                ("perception", (2 if level <= 4 else 3) + 2),
                ("performance", (2 if level <= 4 else 3) + charisma_modifier),
                ("insight", (2 if level <= 4 else 3) + 2),
                ("religion", (2 if level <= 4 else 3) + 1),
            ),
            attacks=(_LYRA_DAGGER,),
            weapon_masteries=(),
            resources=(
                ("bardic-inspiration", charisma_modifier),
                *slot_rows[level],
                ("adrenaline-rush", 2 if level <= 4 else 3),
                ("relentless-endurance", 1),
            ),
            initiative_bonus=0,
        )
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprint at level %s.", level)
        raise


def build_lyra_2024_combat_profiles() -> tuple[PregenCombatProfile, ...]:
    try:
        return tuple(build_lyra_2024_combat_profile(level) for level in (1, 2, 3, 4, 5, 6, 7))
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprints.")
        raise
