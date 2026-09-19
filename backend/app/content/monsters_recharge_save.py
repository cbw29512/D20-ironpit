from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot, SavingThrowAction
from app.domain.combatants import ResourceDefinition
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    OnHitDamage,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.recharge import RechargeRule
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting
from app.domain.traits import CombatTrait


def _row(name: str) -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD source row for {name!r}; found {len(rows)}.")
    return rows[0]


def build_hell_hound() -> CombatantTemplate:
    row = _row("Hell Hound")
    defenses = parse_defense_profile(row)
    raw = str(row["rawText"])
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.I)
    if initiative is None:
        raise ValueError("Hell Hound source is missing Initiative.")

    bite = WeaponAttack(
        id="srd-hell-hound-bite",
        weapon=Weapon(
            id="srd-hell-hound-bite-weapon",
            name="Bite",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=8,
            damage_type=DamageType.PIERCING,
            animation="bite",
            reach_ft=5,
        ),
        attack_bonus=5,
        damage_bonus=3,
        on_hit_damage=[
            OnHitDamage(
                source="Fire",
                dice_count=1,
                dice_size=6,
                damage_bonus=0,
                damage_type=DamageType.FIRE,
            )
        ],
    )
    fire_breath = SavingThrowAction(
        id="srd-hell-hound-fire-breath",
        name="Fire Breath",
        save_ability="dexterity",
        dc=12,
        range_ft=15,
        area=AreaTargeting(shape="cone", origin="self", length_ft=15),
        damage_dice_count=5,
        damage_dice_size=6,
        damage_type="fire",
        success_damage="half",
        resource_id="fire-breath",
    )
    return CombatantTemplate(
        id="srd-hell-hound",
        name="Hell Hound",
        archetype="source-certified monster",
        challenge_rating=str(row["challenge"]).split()[0],
        kind="monster",
        size=CreatureSize.MEDIUM,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)),
        weapon_attack=bite,
        attack_action=AttackActionDefinition(
            id="srd-hell-hound-multiattack",
            name="Multiattack",
            slots=[
                AttackActionSlot(attack_ids=[bite.id]),
                AttackActionSlot(attack_ids=[bite.id]),
            ],
        ),
        saving_throw_actions=[fire_breath],
        combat_traits=[CombatTrait.PACK_TACTICS],
        damage_vulnerabilities=[
            DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])
        ],
        damage_resistances=[
            DamageType(item) for item in sorted(defenses["damage_resistances"])
        ],
        damage_immunities=[
            DamageType(item) for item in sorted(defenses["damage_immunities"])
        ],
        condition_immunities=sorted(defenses["condition_immunities"]),
        resources=[ResourceDefinition(id="fire-breath", name="Fire Breath", max_uses=1)],
        recharge_rules=[RechargeRule(resource_id="fire-breath", minimum_roll=5)],
        visual=VisualLoadout(armor="natural", main_hand="Bite", body_style="monster"),
        source=str(row["sourceReference"]),
    )


def build_recharge_save_monsters() -> list[CombatantTemplate]:
    return [build_hell_hound()]
