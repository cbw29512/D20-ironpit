from __future__ import annotations

import logging

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores

logger = logging.getLogger(__name__)

_SPELL_SLOTS = {
    1: (2,), 2: (3,), 3: (4, 2), 4: (4, 3),
    5: (4, 3, 2), 6: (4, 3, 3), 7: (4, 3, 3, 1), 8: (4, 3, 3, 2),
    9: (4, 3, 3, 3, 1), 10: (4, 3, 3, 3, 2), 11: (4, 3, 3, 3, 2, 1),
    12: (4, 3, 3, 3, 2, 1), 13: (4, 3, 3, 3, 2, 1, 1),
    14: (4, 3, 3, 3, 2, 1, 1), 15: (4, 3, 3, 3, 2, 1, 1, 1),
    16: (4, 3, 3, 3, 2, 1, 1, 1), 17: (4, 3, 3, 3, 2, 1, 1, 1, 1),
    18: (4, 3, 3, 3, 3, 1, 1, 1, 1), 19: (4, 3, 3, 3, 3, 2, 1, 1, 1),
    20: (4, 3, 3, 3, 3, 2, 2, 1, 1),
}


def _abilities(level: int) -> AbilityScores:
    return AbilityScores(
        strength=8,
        dexterity=17 if level >= 19 else 15,
        constitution=18 if level >= 16 else (16 if level >= 12 else 14),
        intelligence=12,
        wisdom=20 if level >= 8 else (18 if level >= 4 else 16),
        charisma=10,
    )


def _resources(level: int) -> tuple[tuple[str, int], ...]:
    resources = [
        (f"spell-slot-{spell_level}", uses)
        for spell_level, uses in enumerate(_SPELL_SLOTS[level], start=1)
        if uses
    ]
    if 2 <= level < 20:
        resources.append(("wild-shape", 2))
    return tuple(resources)


def build_thalen_2014_combat_profile(level: int) -> PregenCombatProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Thalen combat fingerprint covers levels 1 through 20.")
        abilities = _abilities(level)
        pb = 2 + (level - 1) // 4
        con_mod = abilities.modifier("constitution")
        wis_mod = abilities.modifier("wisdom")
        int_mod = abilities.modifier("intelligence")
        return PregenCombatProfile(
            template_id=f"thalen-greenbough-2014-l{level}",
            archetype="Druid",
            level=level,
            abilities=abilities,
            save_proficiencies=("intelligence", "wisdom"),
            armor_class=16 if level >= 19 else 15,
            max_hp=8 + con_mod + (level - 1) * (5 + con_mod),
            speed_ft=35,
            skill_bonuses=(
                ("insight", wis_mod + pb),
                ("religion", int_mod + pb),
                ("perception", wis_mod + pb),
                ("survival", wis_mod + pb),
            ),
            attacks=(AttackExpectation("scimitar", "dexterity", 1, 6, "slashing"),),
            weapon_masteries=(),
            resources=_resources(level),
            damage_immunities=("poison",) if level >= 10 else (),
            unlimited_resources=("wild-shape",) if level >= 20 else (),
        )
    except Exception:
        logger.exception("Failed to compile Thalen's 2014 combat fingerprint at level %s.", level)
        raise


def build_thalen_2014_combat_profiles() -> list[PregenCombatProfile]:
    return [build_thalen_2014_combat_profile(level) for level in range(1, 21)]
