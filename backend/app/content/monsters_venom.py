from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    CombatantTemplate, DamageType, OnHitDamage, Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.size import CreatureSize


def _venom_attack(
    attack_id: str, name: str, bonus: int, base_dice: tuple[int, int, int],
    poison_dice: tuple[int, int], *, reach: int = 5,
) -> WeaponAttack:
    dice_count, dice_size, damage_bonus = base_dice
    poison_count, poison_size = poison_dice
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id, name=name, attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count, dice_size=dice_size, damage_type=DamageType.PIERCING,
            animation="sting" if name == "Sting" else "bite", reach_ft=reach,
        ),
        attack_bonus=bonus,
        damage_bonus=damage_bonus,
        on_hit_damage=[OnHitDamage(
            source="Venom", dice_count=poison_count, dice_size=poison_size,
            damage_type=DamageType.POISON,
        )],
    )


def _monster(
    monster_id: str, name: str, cr: str, ac: int, hp: int, speed: int, initiative: int,
    attack: WeaponAttack, saves: dict[str, int], skills: dict[str, int], body: str,
) -> CombatantTemplate:
    return CombatantTemplate(
        id=monster_id, name=name, archetype=name, challenge_rating=cr, kind="monster",
        size=CreatureSize.MEDIUM, armor_class=ac, max_hp=hp, speed_ft=speed,
        initiative_bonus=initiative, weapon_attack=attack,
        saving_throw_bonuses=saves, skill_bonuses=skills,
        visual=build_monster_visual("natural", attack.weapon.name.lower(), body),
        source=f"SRD 5.2.1 {name} p. 354-355",
    )


def build_venom_monsters() -> list[CombatantTemplate]:
    return [
        _monster(
            "srd-giant-venomous-snake", "Giant Venomous Snake", "1/4", 14, 11, 40, 4,
            _venom_attack("giant-venomous-snake-bite", "Bite", 6, (1, 4, 4), (1, 8), reach=10),
            {"strength": 0, "dexterity": 4, "constitution": 1, "intelligence": -4, "wisdom": 0, "charisma": -4},
            {"athletics": 0, "acrobatics": 4, "perception": 2}, "giant-venomous-snake",
        ),
        _monster(
            "srd-giant-wasp", "Giant Wasp", "1/2", 13, 22, 50, 2,
            _venom_attack("giant-wasp-sting", "Sting", 4, (1, 6, 2), (2, 4)),
            {"strength": 0, "dexterity": 2, "constitution": 0, "intelligence": -5, "wisdom": 0, "charisma": -4},
            {"athletics": 0, "acrobatics": 2}, "giant-wasp",
        ),
        _monster(
            "srd-giant-wolf-spider", "Giant Wolf Spider", "1/4", 13, 11, 40, 3,
            _venom_attack("giant-wolf-spider-bite", "Bite", 5, (1, 4, 3), (2, 4)),
            {"strength": 1, "dexterity": 3, "constitution": 1, "intelligence": -4, "wisdom": 1, "charisma": -3},
            {"athletics": 1, "acrobatics": 3, "perception": 3, "stealth": 7}, "giant-wolf-spider",
        ),
    ]
