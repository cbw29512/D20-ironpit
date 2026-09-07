from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    AttackActionDefinition, AttackActionSlot, ChargeDamage, ChargeDefinition, CombatantTemplate, DamageType,
    Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _attack(
    attack_id: str, name: str, bonus: int, dice_count: int, dice_size: int,
    damage_bonus: int, damage_type: DamageType, *, reach: int = 5,
    prone: CreatureSize | None = None, fixed_damage: int | None = None,
    charge: ChargeDefinition | None = None,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id, name=name, attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count, dice_size=dice_size, damage_type=damage_type,
            animation="bite" if name == "Bite" else "heavy-strike", reach_ft=reach,
        ),
        attack_bonus=bonus, damage_bonus=damage_bonus, knocks_prone_max_size=prone,
        fixed_damage=fixed_damage, charge=charge,
    )


def _charge(maximum: CreatureSize, count: int | None, size: int = 4, damage_type: DamageType = DamageType.BLUDGEONING) -> ChargeDefinition:
    bonus = None if count is None else ChargeDamage(dice_count=count, dice_size=size, damage_type=damage_type)
    return ChargeDefinition(
        minimum_move_ft=20, max_target_size=maximum, prone_max_target_size=maximum, bonus_damage=bonus,
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
               _attack("riding-horse-hooves", "Hooves", 5, 1, 8, 3, DamageType.BLUDGEONING), 360),
        _beast("srd-tiger", "Tiger", "1", CreatureSize.LARGE, 13, 30, 40, 3,
               _attack("tiger-rend", "Rend", 5, 2, 6, 3, DamageType.SLASHING,
                       prone=CreatureSize.LARGE), 362),
        _beast("srd-vulture", "Vulture", "0", CreatureSize.MEDIUM, 10, 5, 50, 0,
               _attack("vulture-beak", "Beak", 2, 1, 4, 0, DamageType.PIERCING), 363,
               traits=(CombatTrait.PACK_TACTICS,)),
        _beast("srd-giant-fire-beetle", "Giant Fire Beetle", "0", CreatureSize.SMALL, 13, 4, 30, 0,
               _attack("giant-fire-beetle-bite", "Bite", 1, 0, 2, 0, DamageType.FIRE, fixed_damage=1),
               351, resistances=(DamageType.FIRE,)),
        _beast("srd-giant-goat", "Giant Goat", "1/2", CreatureSize.LARGE, 11, 19, 40, 1,
               _attack("giant-goat-ram", "Ram", 5, 1, 6, 3, DamageType.BLUDGEONING,
                       charge=_charge(CreatureSize.LARGE, 2)), 351, traits=(CombatTrait.CHARGE,)),
        # Flyby and utility-only spellcasting never alter the no-kiting flat-arena fight.
        _beast("srd-giant-owl", "Giant Owl", "1/4", CreatureSize.LARGE, 12, 19, 60, 2,
               _attack("giant-owl-talons", "Talons", 4, 1, 10, 2, DamageType.SLASHING), 352,
               resistances=(DamageType.NECROTIC, DamageType.RADIANT)),
        _beast("srd-hyena", "Hyena", "0", CreatureSize.MEDIUM, 11, 5, 50, 1,
               _attack("hyena-bite", "Bite", 2, 1, 6, 0, DamageType.PIERCING), 356,
               traits=(CombatTrait.PACK_TACTICS,)),
        _beast("srd-giant-bat", "Giant Bat", "1/4", CreatureSize.LARGE, 13, 22, 60, 3,
               _attack("giant-bat-bite", "Bite", 5, 1, 6, 3, DamageType.PIERCING), 349),
        _beast("srd-mastiff", "Mastiff", "1/8", CreatureSize.MEDIUM, 12, 5, 40, 2,
               _attack("mastiff-bite", "Bite", 3, 1, 6, 1, DamageType.PIERCING,
                       prone=CreatureSize.MEDIUM), 357),
        _beast("srd-mule", "Mule", "1/8", CreatureSize.MEDIUM, 10, 11, 40, 0,
               _attack("mule-hooves", "Hooves", 4, 1, 4, 2, DamageType.BLUDGEONING), 357),
        _beast("srd-rhinoceros", "Rhinoceros", "2", CreatureSize.LARGE, 13, 45, 40, -1,
               _attack("rhinoceros-gore", "Gore", 7, 2, 8, 5, DamageType.PIERCING,
                       charge=_charge(CreatureSize.LARGE, 2, 8, DamageType.PIERCING)), 360,
               traits=(CombatTrait.CHARGE,)),
        _beast("srd-warhorse", "Warhorse", "1/2", CreatureSize.LARGE, 11, 19, 60, 1,
               _attack("warhorse-hooves", "Hooves", 6, 2, 4, 4, DamageType.BLUDGEONING,
                       charge=_charge(CreatureSize.LARGE, 2)), 364, traits=(CombatTrait.CHARGE,)),
    ]
