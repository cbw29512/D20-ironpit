from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    AttackActionDefinition, AttackActionSlot, ChargeDamage, ChargeDefinition, CombatantTemplate,
    DamageType, OnHitDamage, Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _attack(
    attack_id: str, name: str, bonus: int, dice_count: int, dice_size: int,
    damage_bonus: int, damage_type: DamageType, *, reach: int = 5,
    prone_max_size: CreatureSize | None = None, on_hit: list[OnHitDamage] | None = None,
    charge: ChargeDefinition | None = None,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id, name=name, attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count, dice_size=dice_size, damage_type=damage_type,
            animation="bite" if name == "Bite" else "heavy-strike", reach_ft=reach,
        ),
        attack_bonus=bonus, damage_bonus=damage_bonus, knocks_prone_max_size=prone_max_size,
        on_hit_damage=on_hit or [], charge=charge,
    )


def _double(attack: WeaponAttack, monster_id: str) -> AttackActionDefinition:
    return AttackActionDefinition(
        id=f"{monster_id}-multiattack", name="Multiattack",
        slots=[AttackActionSlot(attack_ids=[attack.id]), AttackActionSlot(attack_ids=[attack.id])],
    )


def build_archelon() -> CombatantTemplate:
    bite = _attack("archelon-bite", "Bite", 6, 3, 6, 4, DamageType.PIERCING)
    return CombatantTemplate(
        id="srd-archelon", name="Archelon", archetype="Archelon", challenge_rating="4", kind="monster",
        size=CreatureSize.HUGE, armor_class=17, max_hp=90, speed_ft=20, initiative_bonus=3,
        weapon_attack=bite, attack_action=_double(bite, "archelon"),
        visual=build_monster_visual("shell", "bite", "archelon"), source="SRD 5.2.1 Archelon p. 345",
    )


def build_ankylosaurus() -> CombatantTemplate:
    tail = _attack("ankylosaurus-tail", "Tail", 6, 1, 10, 4, DamageType.BLUDGEONING,
                   reach=10, prone_max_size=CreatureSize.HUGE)
    return CombatantTemplate(
        id="srd-ankylosaurus", name="Ankylosaurus", archetype="Ankylosaurus", challenge_rating="3", kind="monster",
        size=CreatureSize.HUGE, armor_class=15, max_hp=68, speed_ft=30, initiative_bonus=0,
        weapon_attack=tail, attack_action=_double(tail, "ankylosaurus"),
        visual=build_monster_visual("natural", "tail", "ankylosaurus"), source="SRD 5.2.1 Ankylosaurus p. 344",
    )


def build_giant_eagle() -> CombatantTemplate:
    rend = _attack(
        "giant-eagle-rend", "Rend", 5, 1, 4, 3, DamageType.SLASHING,
        on_hit=[OnHitDamage(source="Radiant", dice_count=1, dice_size=6, damage_type=DamageType.RADIANT)],
    )
    return CombatantTemplate(
        id="srd-giant-eagle", name="Giant Eagle", archetype="Giant Eagle", challenge_rating="1", kind="monster",
        size=CreatureSize.LARGE, armor_class=13, max_hp=26, speed_ft=80, initiative_bonus=3,
        weapon_attack=rend, attack_action=_double(rend, "giant-eagle"),
        damage_resistances=[DamageType.NECROTIC, DamageType.RADIANT],
        visual=build_monster_visual("feathers", "talons", "giant-eagle"), source="SRD 5.2.1 Giant Eagle p. 351",
    )


def build_giant_elk() -> CombatantTemplate:
    ram = _attack(
        "giant-elk-ram", "Ram", 6, 2, 6, 4, DamageType.BLUDGEONING, reach=10,
        on_hit=[OnHitDamage(source="Radiant", dice_count=2, dice_size=4, damage_type=DamageType.RADIANT)],
        charge=ChargeDefinition(
            minimum_move_ft=20, max_target_size=CreatureSize.HUGE, prone_max_target_size=CreatureSize.HUGE,
            bonus_damage=ChargeDamage(dice_count=2, dice_size=4, damage_type=DamageType.BLUDGEONING),
        ),
    )
    return CombatantTemplate(
        id="srd-giant-elk", name="Giant Elk", archetype="Giant Elk", challenge_rating="2", kind="monster",
        size=CreatureSize.HUGE, armor_class=14, max_hp=42, speed_ft=60, initiative_bonus=6,
        weapon_attack=ram, combat_traits=[CombatTrait.CHARGE],
        damage_resistances=[DamageType.NECROTIC, DamageType.RADIANT],
        visual=build_monster_visual("fur", "antlers", "giant-elk"), source="SRD 5.2.1 Giant Elk p. 351",
    )


def build_expansion_four() -> list[CombatantTemplate]:
    return [build_archelon(), build_ankylosaurus(), build_giant_eagle(), build_giant_elk()]
