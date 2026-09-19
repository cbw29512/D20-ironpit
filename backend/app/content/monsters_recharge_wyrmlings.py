from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot, SavingThrowAction
from app.domain.combatants import ResourceDefinition
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.recharge import RechargeRule
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting

_PROFILES = {
    "Black Dragon Wyrmling": (4, 6, 2, 1, 4, "acid", "Acid Breath", "dexterity", 11, 5, 8, "acid", "line", 15, 5),
    "Blue Dragon Wyrmling": (5, 10, 3, 1, 6, "lightning", "Lightning Breath", "dexterity", 12, 6, 6, "lightning", "line", 30, 5),
    "Green Dragon Wyrmling": (4, 10, 2, 1, 6, "poison", "Poison Breath", "constitution", 11, 6, 6, "poison", "cone", 15, None),
    "Red Dragon Wyrmling": (6, 10, 4, 1, 6, "fire", "Fire Breath", "dexterity", 13, 7, 6, "fire", "cone", 15, None),
    "White Dragon Wyrmling": (4, 8, 2, 1, 4, "cold", "Cold Breath", "constitution", 12, 5, 8, "cold", "cone", 15, None),
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _row(name: str) -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD source row for {name!r}; found {len(rows)}.")
    return rows[0]


def _build(name: str) -> CombatantTemplate:
    row = _row(name)
    (
        attack_bonus, rend_size, damage_bonus, extra_count, extra_size, extra_type,
        breath_name, save_ability, dc, breath_count, breath_size, breath_type,
        shape, length_ft, width_ft,
    ) = _PROFILES[name]
    monster_id = f"srd-{_slug(name)}"
    resource_id = _slug(breath_name)
    defenses = parse_defense_profile(row)
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError(f"{name} source is missing Initiative.")
    rend = WeaponAttack(
        id=f"{monster_id}-rend",
        weapon=Weapon(
            id=f"{monster_id}-rend-weapon", name="Rend", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=rend_size, damage_type=DamageType.SLASHING,
            animation="claw", reach_ft=5,
        ),
        attack_bonus=attack_bonus, damage_bonus=damage_bonus,
        on_hit_damage=[
            OnHitDamage(
                source=extra_type.title(), dice_count=extra_count, dice_size=extra_size,
                damage_bonus=0, damage_type=DamageType(extra_type),
            )
        ],
    )
    area = (
        AreaTargeting(shape="line", origin="self", length_ft=length_ft, width_ft=width_ft)
        if shape == "line"
        else AreaTargeting(shape="cone", origin="self", length_ft=length_ft)
    )
    breath = SavingThrowAction(
        id=f"{monster_id}-{resource_id}", name=breath_name, save_ability=save_ability, dc=dc,
        range_ft=length_ft, area=area, damage_dice_count=breath_count,
        damage_dice_size=breath_size, damage_type=breath_type, success_damage="half",
        resource_id=resource_id,
    )
    return CombatantTemplate(
        id=monster_id, name=name, archetype="source-certified monster",
        challenge_rating=str(row["challenge"]).split()[0], kind="monster", size=CreatureSize.MEDIUM,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)), weapon_attack=rend,
        attack_action=AttackActionDefinition(
            id=f"{monster_id}-multiattack", name="Multiattack",
            slots=[AttackActionSlot(attack_ids=[rend.id]), AttackActionSlot(attack_ids=[rend.id])],
        ),
        saving_throw_actions=[breath],
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        resources=[ResourceDefinition(id=resource_id, name=breath_name, max_uses=1)],
        recharge_rules=[RechargeRule(resource_id=resource_id, minimum_roll=5)],
        visual=VisualLoadout(armor="scales", main_hand="Rend", body_style="dragon"),
        source=str(row["sourceReference"]),
    )


def build_recharge_wyrmlings() -> list[CombatantTemplate]:
    return [_build(name) for name in _PROFILES]
