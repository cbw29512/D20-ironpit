from __future__ import annotations

from app.content.pregen_combat_profiles import AttackExpectation, PregenCombatProfile
from app.content.rogue_combat_levels import ROGUE_COMBAT_LEVELS
from app.domain.character_builds import AbilityScores


def build_mara_quickstep_combat_profile(level: int = 1) -> PregenCombatProfile:
    """Build Mara's immutable expected combat fingerprint for a certified Rogue level."""
    if level not in ROGUE_COMBAT_LEVELS:
        raise ValueError(f"Mara Rogue level {level} must be between 1 and 20.")

    row = ROGUE_COMBAT_LEVELS[level]
    dexterity = 18 if level >= 4 else 17
    constitution = 16 if level >= 4 else 15
    dexterity_mod = (dexterity - 10) // 2
    hp = 10 + 7 * (level - 1)
    if level >= 4:
        hp += level

    return PregenCombatProfile(
        template_id=f"mara-quickstep-l{level}",
        archetype="Rogue",
        level=level,
        abilities=AbilityScores(
            strength=13,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=10,
            wisdom=10,
            charisma=10,
        ),
        save_proficiencies=("dexterity", "intelligence"),
        armor_class=11 + dexterity_mod,
        max_hp=hp,
        speed_ft=30,
        skill_bonuses=(
            ("athletics", 1 + row.proficiency_bonus),
            ("acrobatics", dexterity_mod + row.proficiency_bonus),
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
        resources=(("adrenaline-rush", row.proficiency_bonus), ("relentless-endurance", 1)),
        sneak_attack_d6=row.sneak_attack_d6,
    )
