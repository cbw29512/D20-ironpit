from __future__ import annotations

from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind


def build_seraphine_mace_attack(attack_bonus: int) -> WeaponAttack:
    return WeaponAttack(
        id="seraphine-mace",
        weapon=Weapon(
            id="mace",
            name="Mace",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.BLUDGEONING,
            animation="blunt-strike",
            reach_ft=5,
        ),
        attack_bonus=attack_bonus,
        damage_bonus=0,
    )


def seraphine_saving_throw_bonuses(
    proficiency_bonus: int,
    wisdom_modifier: int,
    charisma_modifier: int,
) -> dict[str, int]:
    return {
        "strength": 0,
        "dexterity": 0,
        "constitution": 0,
        "intelligence": 2,
        "wisdom": proficiency_bonus + wisdom_modifier,
        "charisma": proficiency_bonus + charisma_modifier,
    }


def seraphine_skill_bonuses(
    proficiency_bonus: int,
    wisdom_modifier: int,
    charisma_modifier: int,
) -> dict[str, int]:
    return {
        "athletics": 0,
        "acrobatics": 0,
        "arcana": proficiency_bonus + 2,
        "history": proficiency_bonus + 2,
        "medicine": proficiency_bonus + wisdom_modifier,
        "persuasion": proficiency_bonus + charisma_modifier,
    }
