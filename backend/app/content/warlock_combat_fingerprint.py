from __future__ import annotations

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.domain.character_builds import AbilityScores


def build_varek_ashenmark_combat_profile() -> PregenCombatProfile:
    return PregenCombatProfile(
        template_id="varek-ashenmark-l1",
        archetype="Warlock",
        level=1,
        abilities=AbilityScores(
            strength=10,
            dexterity=10,
            constitution=10,
            intelligence=13,
            wisdom=15,
            charisma=17,
        ),
        save_proficiencies=("wisdom", "charisma"),
        armor_class=11,
        max_hp=8,
        speed_ft=30,
        skill_bonuses=(
            ("athletics", 0),
            ("acrobatics", 0),
            ("arcana", 3),
            ("intimidation", 5),
            ("insight", 4),
            ("religion", 3),
        ),
        attacks=(
            AttackExpectation(
                weapon_id="longsword",
                ability="charisma",
                dice_count=1,
                dice_size=8,
                damage_type="slashing",
            ),
        ),
        weapon_masteries=(),
        resources=(("pact-slot-1", 1), ("adrenaline-rush", 2), ("relentless-endurance", 1)),
    )
