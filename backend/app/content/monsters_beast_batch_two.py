from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    AttackActionDefinition, AttackActionSlot, CombatantTemplate, DamageType,
    Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _attack(
    attack_id: str, name: str, bonus: int, dice_count: int, dice_size: int,
    damage_bonus: int, damage_type: DamageType, *, reach: int = 5,
    prone: CreatureSize | None = None,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id, name=name, attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count, dice_size=dice_size, damage_type=damage_type,
            animation="bite" if name == "Bite" else "heavy-strike", reach_ft=reach,
        ),
        attack_bonus=bonus, damage_bonus=damage_bonus, knocks_prone_max_size=prone,
    )


def _beast(
    monster_id: str, name: str, cr: str, size: CreatureSize, ac: int, hp: int,
    speed: int, initiative: int, attack: WeaponAttack, page: int, *,
    traits: tuple[CombatTrait, ...] = (), resistances: tuple[DamageType, ...] = (),
    multiattack: bool = False,
) -> CombatantTemplate:
    action = None
    if multiattack:
        action = AttackActionDefinition(
            id=f"{monster_id}-multiattack", name="Multiattack",
            slots=[AttackActionSlot(attack_ids=[attack.id]), AttackActionSlot(attack_ids=[attack.id])],
        )
    return CombatantTemplate(
        id=monster_id, name=name, archetype=name, challenge_rating=cr, kind="monster",
        size=size, armor_class=ac, max_hp=hp, speed_ft=speed, initiative_bonus=initiative,
        weapon_attack=attack, attack_action=action, combat_traits=list(traits),
        damage_resistances=list(resistances),
        visual=build_monster_visual("natural", attack.weapon.name.lower(), name.lower().replace(" ", "-")),
        source=f"SRD 5.2.1 {name} p. {page}",
    )


def build_beast_batch_two() -> list[CombatantTemplate]:
    return [
        _beast("srd-eagle", "Eagle", "0", CreatureSize.SMALL, 12, 4, 60, 2,
               _attack("eagle-talons", "Talons", 4, 1, 4, 2, DamageType.SLASHING), 347),
        _beast("srd-panther", "Panther", "1/4", CreatureSize.MEDIUM, 13, 13, 50, 3,
               _attack("panther-rend", "Rend", 5, 1, 6, 3, DamageType.SLASHING), 357),
        _beast("srd-plesiosaurus", "Plesiosaurus", "2", CreatureSize.LARGE, 13, 68, 20, 2,
               _attack("plesiosaurus-bite", "Bite", 6, 2, 6, 4, DamageType.PIERCING, reach=10), 358),
        _beast("srd-polar-bear", "Polar Bear", "2", CreatureSize.LARGE, 12, 42, 40, 2,
               _attack("polar-bear-rend", "Rend", 7, 1, 8, 5, DamageType.SLASHING), 358,
               resistances=(DamageType.COLD,), multiattack=True),
        _beast("srd-pony", "Pony", "1/8", CreatureSize.MEDIUM, 10, 11, 40, 0,
               _attack("pony-hooves", "Hooves", 4, 1, 4, 2, DamageType.BLUDGEONING), 358),
        _beast("srd-pteranodon", "Pteranodon", "1/4", CreatureSize.MEDIUM, 13, 13, 60, 2,
               _attack("pteranodon-bite", "Bite", 4, 1, 8, 2, DamageType.PIERCING), 358),
        _beast("srd-riding-horse", "Riding Horse", "1/4", CreatureSize.LARGE, 11, 13, 60, 1,
               _attack("riding-horse-hooves", "Hooves", 5, 1, 8, 3, DamageType.BLUDGEONING), 359),
        _beast("srd-tiger", "Tiger", "1", CreatureSize.LARGE, 13, 30, 40, 3,
               _attack("tiger-rend", "Rend", 5, 2, 6, 3, DamageType.SLASHING,
                       prone=CreatureSize.LARGE), 362),
        _beast("srd-vulture", "Vulture", "0", CreatureSize.MEDIUM, 10, 5, 50, 0,
               _attack("vulture-beak", "Beak", 2, 1, 4, 0, DamageType.PIERCING), 363,
               traits=(CombatTrait.PACK_TACTICS,)),
    ]
