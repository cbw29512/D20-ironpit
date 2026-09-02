from __future__ import annotations

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores


def build_mara_quickstep_combat_profile() -> PregenCombatProfile:
    return PregenCombatProfile(
        template_id="mara-quickstep-l1",
        archetype="Rogue",
        level=1,
        abilities=AbilityScores(
            strength=13, dexterity=17, constitution=15,
            intelligence=10, wisdom=10, charisma=10,
        ),
        save_proficiencies=("dexterity", "intelligence"),
        armor_class=14,
        max_hp=10,
        speed_ft=30,
        skill_bonuses=(("acrobatics", 5),),
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
        sneak_attack_d6=1,
    )
