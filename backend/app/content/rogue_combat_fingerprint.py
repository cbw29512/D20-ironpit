from __future__ import annotations

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores


def _build_mara_quickstep_combat_profile(level: int) -> PregenCombatProfile:
    try:
        return PregenCombatProfile(
            template_id=f"mara-quickstep-l{level}",
            archetype="Rogue",
            level=level,
            abilities=AbilityScores(
                strength=13, dexterity=17, constitution=15,
                intelligence=10, wisdom=10, charisma=10,
            ),
            save_proficiencies=("dexterity", "intelligence"),
            armor_class=14,
            max_hp=10 + ((level - 1) * 7),
            speed_ft=30,
            skill_bonuses=(("athletics", 3), ("acrobatics", 5)),
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
            resources=(("adrenaline-rush", 2), ("relentless-endurance", 1)),
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
