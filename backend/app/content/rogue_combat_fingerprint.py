from __future__ import annotations

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores


def _build_mara_quickstep_combat_profile(level: int) -> PregenCombatProfile:
    try:
        dexterity = 20 if level >= 8 else (18 if level >= 4 else 17)
        constitution = 20 if level >= 12 else (18 if level >= 10 else (16 if level >= 4 else 15))
        dexterity_mod = (dexterity - 10) // 2
        constitution_mod = (constitution - 10) // 2
        wisdom = 12 if level >= 16 else 10
        proficiency_bonus = 2 + (level - 1) // 4
        return PregenCombatProfile(
            template_id=f"mara-quickstep-l{level}",
            archetype="Rogue",
            level=level,
            abilities=AbilityScores(
                strength=13, dexterity=dexterity, constitution=constitution,
                intelligence=10, wisdom=wisdom, charisma=10,
            ),
            save_proficiencies=(
                ("dexterity", "intelligence", "wisdom", "charisma")
                if level >= 15 else ("dexterity", "intelligence")
            ),
            armor_class=11 + dexterity_mod,
            max_hp=8 + constitution_mod + (level - 1) * (5 + constitution_mod),
            speed_ft=30,
            skill_bonuses=(
                ("athletics", proficiency_bonus + 1),
                ("acrobatics", proficiency_bonus + dexterity_mod),
            ),
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
            resources=(("adrenaline-rush", proficiency_bonus), ("relentless-endurance", 1)),
            sneak_attack_d6=(level + 1) // 2,
        )
    except Exception as exc:
        raise RuntimeError(f"Mara Rogue level {level} combat profile could not be created.") from exc


def build_mara_quickstep_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(1)


def build_mara_quickstep_level2_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(2)


def build_mara_quickstep_level3_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(3)



def build_mara_quickstep_level4_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(4)


def build_mara_quickstep_level5_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(5)


def build_mara_quickstep_level6_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(6)


def build_mara_quickstep_level7_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(7)


def build_mara_quickstep_level8_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(8)


def build_mara_quickstep_level9_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(9)



def build_mara_quickstep_level10_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(10)



def build_mara_quickstep_level11_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(11)



def build_mara_quickstep_level12_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(12)



def build_mara_quickstep_level13_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(13)



def build_mara_quickstep_level14_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(14)



def build_mara_quickstep_level15_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(15)



def build_mara_quickstep_level16_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(16)



def build_mara_quickstep_combat_profiles(max_level: int) -> list[PregenCombatProfile]:
    """Return the cumulative independent fingerprints through max_level."""
    if max_level < 1 or max_level > 20:
        raise ValueError("Rogue combat profile max_level must be between 1 and 20.")
    return [_build_mara_quickstep_combat_profile(level) for level in range(1, max_level + 1)]



def build_mara_quickstep_level17_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(17)



def build_mara_quickstep_level18_combat_profile() -> PregenCombatProfile:
    return _build_mara_quickstep_combat_profile(18)
