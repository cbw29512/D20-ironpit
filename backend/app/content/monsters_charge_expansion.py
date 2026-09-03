from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, DamageType, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _attack(
    attack_id: str,
    name: str,
    bonus: int,
    dice_count: int,
    dice_size: int,
    damage_bonus: int,
    damage_type: DamageType,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=f"{attack_id}-weapon",
            name=name,
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count,
            dice_size=dice_size,
            damage_type=damage_type,
            animation="heavy-strike",
            reach_ft=5,
        ),
        attack_bonus=bonus,
        damage_bonus=damage_bonus,
    )


def build_minotaur_skeleton() -> CombatantTemplate:
    gore = _attack("minotaur-skeleton-gore", "Gore", 6, 2, 6, 4, DamageType.PIERCING)
    slam = _attack("minotaur-skeleton-slam", "Slam", 6, 2, 10, 4, DamageType.BLUDGEONING)
    return CombatantTemplate(
        id="srd-minotaur-skeleton",
        name="Minotaur Skeleton",
        archetype="Minotaur Skeleton",
        challenge_rating="2",
        kind="monster",
        size=CreatureSize.LARGE,
        armor_class=12,
        max_hp=45,
        speed_ft=40,
        initiative_bonus=0,
        weapon_attack=gore,
        alternate_weapon_attacks=[slam],
        combat_traits=[CombatTrait.CHARGE],
        damage_vulnerabilities=[DamageType.BLUDGEONING],
        damage_immunities=[DamageType.POISON],
        condition_immunities=["exhaustion", "poisoned"],
        visual=build_monster_visual("bones", "horns", "minotaur-skeleton"),
        source="SRD 5.2.1 Minotaur Skeleton p. 326",
    )


def build_triceratops() -> CombatantTemplate:
    gore = _attack("triceratops-gore", "Gore", 9, 2, 12, 6, DamageType.PIERCING)
    multiattack = AttackActionDefinition(
        id="triceratops-multiattack",
        name="Multiattack",
        slots=[
            AttackActionSlot(attack_ids=[gore.id]),
            AttackActionSlot(attack_ids=[gore.id]),
        ],
    )
    return CombatantTemplate(
        id="srd-triceratops",
        name="Triceratops",
        archetype="Triceratops",
        challenge_rating="5",
        kind="monster",
        size=CreatureSize.HUGE,
        armor_class=14,
        max_hp=114,
        speed_ft=50,
        initiative_bonus=-1,
        weapon_attack=gore,
        attack_action=multiattack,
        combat_traits=[CombatTrait.CHARGE],
        visual=build_monster_visual("hide", "horns", "triceratops"),
        source="SRD 5.2.1 Triceratops p. 363",
    )


def build_warhorse_skeleton() -> CombatantTemplate:
    hooves = _attack("warhorse-skeleton-hooves", "Hooves", 6, 1, 6, 4, DamageType.BLUDGEONING)
    return CombatantTemplate(
        id="srd-warhorse-skeleton",
        name="Warhorse Skeleton",
        archetype="Warhorse Skeleton",
        challenge_rating="1/2",
        kind="monster",
        size=CreatureSize.LARGE,
        armor_class=13,
        max_hp=22,
        speed_ft=60,
        initiative_bonus=1,
        weapon_attack=hooves,
        combat_traits=[CombatTrait.CHARGE],
        damage_vulnerabilities=[DamageType.BLUDGEONING],
        damage_immunities=[DamageType.POISON],
        condition_immunities=["exhaustion", "poisoned"],
        visual=build_monster_visual("bones", "hooves", "warhorse-skeleton"),
        source="SRD 5.2.1 Warhorse Skeleton p. 326",
    )


def build_charge_expansion() -> list[CombatantTemplate]:
    return [build_minotaur_skeleton(), build_triceratops(), build_warhorse_skeleton()]
