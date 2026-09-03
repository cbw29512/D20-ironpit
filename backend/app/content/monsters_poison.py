from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import (
    CombatantTemplate, DamageType, HitControlEffect, OnHitDamage,
    Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _attack(
    attack_id: str, name: str, bonus: int, count: int, size: int, damage_bonus: int,
    damage_type: DamageType, *, reach: int = 5, poison_dice: int = 0,
    poison_timing: str | None = None,
) -> WeaponAttack:
    control = HitControlEffect(condition_id="poisoned", expiry_timing=poison_timing) if poison_timing else None
    extra = [OnHitDamage(
        source="Poison", dice_count=poison_dice, dice_size=6,
        damage_bonus=0, damage_type=DamageType.POISON,
    )] if poison_dice else []
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id, name=name, attack_kind=WeaponAttackKind.MELEE,
            dice_count=count, dice_size=size, damage_type=damage_type,
            animation="bite" if name == "Bite" else "strike", reach_ft=reach,
        ),
        attack_bonus=bonus, damage_bonus=damage_bonus,
        on_hit_damage=extra, control_effect=control,
    )


def build_giant_centipede() -> CombatantTemplate:
    bite = _attack(
        "giant-centipede-bite", "Bite", 4, 1, 4, 2, DamageType.PIERCING,
        poison_timing="source_turn_start",
    )
    return CombatantTemplate(
        id="srd-giant-centipede", name="Giant Centipede", archetype="Giant Centipede",
        challenge_rating="1/4", kind="monster", size=CreatureSize.SMALL,
        armor_class=14, max_hp=9, speed_ft=30, initiative_bonus=2,
        weapon_attack=bite,
        saving_throw_bonuses={
            "strength": -3, "dexterity": 2, "constitution": 1,
            "intelligence": -5, "wisdom": -2, "charisma": -4,
        },
        skill_bonuses={"athletics": -3, "acrobatics": 2},
        visual=build_monster_visual("natural", "bite", "giant-centipede"),
        source="SRD 5.2.1 Giant Centipede p. 349",
    )


def build_giant_vulture() -> CombatantTemplate:
    gouge = _attack(
        "giant-vulture-gouge", "Gouge", 4, 2, 6, 2, DamageType.PIERCING,
        poison_timing="target_turn_end",
    )
    return CombatantTemplate(
        id="srd-giant-vulture", name="Giant Vulture", archetype="Giant Vulture",
        challenge_rating="1", kind="monster", size=CreatureSize.LARGE,
        armor_class=10, max_hp=25, speed_ft=60, initiative_bonus=0,
        weapon_attack=gouge, combat_traits=[CombatTrait.PACK_TACTICS],
        damage_resistances=[DamageType.NECROTIC], skill_bonuses={"perception": 3},
        visual=build_monster_visual("natural", "beak", "giant-vulture"),
        source="SRD 5.2.1 Giant Vulture p. 354",
    )


def build_wyvern() -> CombatantTemplate:
    bite = _attack("wyvern-bite", "Bite", 7, 2, 8, 4, DamageType.PIERCING)
    sting = _attack(
        "wyvern-sting", "Sting", 7, 2, 6, 4, DamageType.PIERCING,
        reach=10, poison_dice=7, poison_timing="source_turn_start",
    )
    multiattack = AttackActionDefinition(
        id="wyvern-multiattack", name="Multiattack",
        slots=[AttackActionSlot(attack_ids=[bite.id]), AttackActionSlot(attack_ids=[sting.id])],
    )
    return CombatantTemplate(
        id="srd-wyvern", name="Wyvern", archetype="Wyvern", challenge_rating="6",
        kind="monster", size=CreatureSize.LARGE, armor_class=14, max_hp=127,
        speed_ft=80, initiative_bonus=0, weapon_attack=bite,
        alternate_weapon_attacks=[sting], attack_action=multiattack,
        skill_bonuses={"perception": 4},
        visual=build_monster_visual("natural", "sting", "wyvern"),
        source="SRD 5.2.1 Wyvern p. 343",
    )


def build_poison_monsters() -> list[CombatantTemplate]:
    return [build_giant_centipede(), build_giant_vulture(), build_wyvern()]
