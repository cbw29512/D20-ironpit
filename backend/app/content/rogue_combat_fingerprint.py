from __future__ import annotations

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.rogue_combat_levels import ROGUE_COMBAT_LEVELS
from app.domain.character_builds import AbilityScores


def _scores(level: int) -> AbilityScores:
    return AbilityScores(
        strength=13,
        dexterity=18 if level >= 4 else 17,
        constitution=16 if level >= 4 else 15,
        intelligence=10,
        wisdom=10,
        charisma=10,
    )


def _max_hp(level: int) -> int:
    hp = 10 + 7 * (level - 1)
    return hp + level if level >= 4 else hp


def build_mara_quickstep_combat_profile(level: int = 1) -> PregenCombatProfile:
    if level not in range(1, 5):
        raise ValueError("Mara combat fingerprint currently certifies Rogue levels 1 through 4.")
    row = ROGUE_COMBAT_LEVELS[level]
    abilities = _scores(level)
    dexterity_mod = abilities.modifier("dexterity")
    return PregenCombatProfile(
        template_id=f"mara-quickstep-l{level}",
        archetype="Rogue",
        level=level,
        abilities=abilities,
        save_proficiencies=("dexterity", "intelligence"),
        armor_class=11 + dexterity_mod,
        max_hp=_max_hp(level),
        speed_ft=30,
        skill_bonuses=(("athletics", 1 + row.proficiency_bonus), ("acrobatics", dexterity_mod + row.proficiency_bonus)),
        attacks=(
            AttackExpectation(
                "shortsword", "dexterity", 1, 6, "piercing",
                mastery_property="Vex", sneak_attack_eligible=True,
            ),
            AttackExpectation(
                "shortbow", "dexterity", 1, 6, "piercing",
                normal_range_ft=80, long_range_ft=320,
                mastery_property="Vex", sneak_attack_eligible=True,
            ),
        ),
        weapon_masteries=("shortsword", "shortbow"),
        resources=(("adrenaline-rush", row.proficiency_bonus), ("relentless-endurance", 1)),
        sneak_attack_d6=row.sneak_attack_d6,
    )
