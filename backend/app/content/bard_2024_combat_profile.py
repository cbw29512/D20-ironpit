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


def build_lyra_2024_combat_profile(level: int) -> PregenCombatProfile:
    """Independent source-derived combat fingerprint for the certified Bard foundation."""
    try:
        if level not in {1, 2}:
            raise ValueError("2024 Lyra combat fingerprint currently covers levels 1 through 2.")
        acrobatics = 2 if level == 1 else 4
        spell_slots = 2 if level == 1 else 3
        max_hp = 8 if level == 1 else 13
        return PregenCombatProfile(
            template_id=f"lyra-silverstring-l{level}",
            archetype="Bard",
            level=level,
            abilities=_LYRA_2024_ABILITIES,
            save_proficiencies=("dexterity", "charisma"),
            armor_class=12,
            max_hp=max_hp,
            speed_ft=30,
            skill_bonuses=(
                ("athletics", 0),
                ("acrobatics", acrobatics),
                ("perception", 4),
                ("performance", 5),
                ("insight", 4),
                ("religion", 3),
            ),
            attacks=(_LYRA_DAGGER,),
            weapon_masteries=(),
            resources=(
                ("bardic-inspiration", 3),
                ("spell-slot-1", spell_slots),
                ("adrenaline-rush", 2),
                ("relentless-endurance", 1),
            ),
            initiative_bonus=0,
        )
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprint at level %s.", level)
        raise


def build_lyra_2024_combat_profiles() -> tuple[PregenCombatProfile, ...]:
    try:
        return tuple(build_lyra_2024_combat_profile(level) for level in (1, 2))
    except Exception:
        logger.exception("Failed to build 2024 Lyra combat fingerprints.")
        raise
