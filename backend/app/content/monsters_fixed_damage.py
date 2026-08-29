from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import CombatantTemplate, DamageType, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize


def _attack(attack_id: str, name: str, bonus: int, damage_type: DamageType, animation: str) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id,
            name=name,
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=0,
            dice_size=2,
            damage_type=damage_type,
            animation=animation,
        ),
        attack_bonus=bonus,
        damage_bonus=0,
        fixed_damage=1,
    )


def _monster(
    monster_id: str,
    name: str,
    size: CreatureSize,
    ac: int,
    hp: int,
    speed: int,
    initiative: int,
    attack: WeaponAttack,
    page: int,
    *,
    resistances: tuple[DamageType, ...] = (),
    vulnerabilities: tuple[DamageType, ...] = (),
) -> CombatantTemplate:
    return CombatantTemplate(
        id=monster_id,
        name=name,
        archetype=name,
        challenge_rating="0",
        kind="monster",
        size=size,
        armor_class=ac,
        max_hp=hp,
        speed_ft=speed,
        initiative_bonus=initiative,
        weapon_attack=attack,
        damage_resistances=list(resistances),
        damage_vulnerabilities=list(vulnerabilities),
        visual=build_monster_visual("natural", attack.weapon.name.lower(), name.lower().replace(" ", "-")),
        source=f"SRD 5.2.1 {name} p. {page}",
    )


def build_fixed_damage_monsters() -> list[CombatantTemplate]:
    return [
        _monster("srd-awakened-shrub", "Awakened Shrub", CreatureSize.SMALL, 9, 10, 20, -1,
                 _attack("awakened-shrub-rake", "Rake", 1, DamageType.SLASHING, "heavy-slash"), 260,
                 resistances=(DamageType.PIERCING,), vulnerabilities=(DamageType.FIRE,)),
        _monster("srd-badger", "Badger", CreatureSize.TINY, 11, 5, 20, 0,
                 _attack("badger-bite", "Bite", 2, DamageType.PIERCING, "bite"), 345,
                 resistances=(DamageType.POISON,)),
        _monster("srd-bat", "Bat", CreatureSize.TINY, 12, 1, 30, 2,
                 _attack("bat-bite", "Bite", 4, DamageType.PIERCING, "bite"), 345),
        _monster("srd-cat", "Cat", CreatureSize.TINY, 12, 2, 40, 2,
                 _attack("cat-scratch", "Scratch", 4, DamageType.SLASHING, "slash"), 346),
        _monster("srd-crab", "Crab", CreatureSize.TINY, 11, 3, 20, 0,
                 _attack("crab-claw", "Claw", 2, DamageType.BLUDGEONING, "heavy-strike"), 346),
        _monster("srd-frog", "Frog", CreatureSize.TINY, 11, 1, 20, 1,
                 _attack("frog-bite", "Bite", 3, DamageType.PIERCING, "bite"), 348),
        _monster("srd-hawk", "Hawk", CreatureSize.TINY, 13, 1, 60, 3,
                 _attack("hawk-talons", "Talons", 5, DamageType.SLASHING, "slash"), 355),
        _monster("srd-lizard", "Lizard", CreatureSize.TINY, 10, 2, 20, 0,
                 _attack("lizard-bite", "Bite", 2, DamageType.PIERCING, "bite"), 357),
        _monster("srd-owl", "Owl", CreatureSize.TINY, 11, 1, 60, 1,
                 _attack("owl-talons", "Talons", 3, DamageType.SLASHING, "slash"), 358),
        _monster("srd-rat", "Rat", CreatureSize.TINY, 10, 1, 20, 0,
                 _attack("rat-bite", "Bite", 2, DamageType.PIERCING, "bite"), 359),
        _monster("srd-raven", "Raven", CreatureSize.TINY, 12, 2, 50, 2,
                 _attack("raven-beak", "Beak", 4, DamageType.PIERCING, "bite"), 359),
        _monster("srd-weasel", "Weasel", CreatureSize.TINY, 13, 1, 30, 3,
                 _attack("weasel-bite", "Bite", 5, DamageType.PIERCING, "bite"), 364),
    ]
