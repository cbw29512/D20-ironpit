from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import SavingThrowAction
from app.domain.combatants import ResourceDefinition
from app.domain.models import CombatantTemplate, DamageType, VisualLoadout
from app.domain.recharge import RechargeRule
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting


def _row(name: str) -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD source row for {name!r}; found {len(rows)}.")
    return rows[0]


def _base_template(name: str, size: CreatureSize, visual_hand: str) -> CombatantTemplate:
    row = _row(name)
    defenses = parse_defense_profile(row)
    raw = str(row["rawText"])
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.I)
    if initiative is None:
        raise ValueError(f"{name} source is missing Initiative.")
    return CombatantTemplate(
        id=f"srd-{name.lower().replace(' ', '-')}",
        name=name,
        archetype="source-certified monster",
        challenge_rating=str(row["challenge"]).split()[0],
        kind="monster",
        size=size,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)),
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="natural", main_hand=visual_hand, body_style="monster"),
        source=str(row["sourceReference"]),
    )


def build_behir() -> CombatantTemplate:
    template = _base_template("Behir", CreatureSize.HUGE, "Bite")
    breath = SavingThrowAction(
        id="srd-behir-lightning-breath",
        name="Lightning Breath",
        save_ability="dexterity",
        dc=16,
        range_ft=20,
        area=AreaTargeting(shape="line", origin="self", length_ft=20, width_ft=5),
        damage_dice_count=12,
        damage_dice_size=10,
        damage_type="lightning",
        success_damage="half",
        resource_id="lightning-breath",
    )
    template.saving_throw_actions = [breath]
    template.resources = [ResourceDefinition(id="lightning-breath", name="Lightning Breath", max_uses=1)]
    template.recharge_rules = [RechargeRule(resource_id="lightning-breath", minimum_roll=5)]
    return template


def build_vrock() -> CombatantTemplate:
    template = _base_template("Vrock", CreatureSize.LARGE, "Beak")
    spores = SavingThrowAction(
        id="srd-vrock-spores",
        name="Spores",
        save_ability="constitution",
        dc=14,
        range_ft=15,
        area=AreaTargeting(shape="radius", origin="self", radius_ft=15),
        damage_dice_count=0,
        success_damage="none",
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="poisoned",
            expiry_timing="target_turn_end",
            repeat_save_ability="constitution",
            repeat_save_dc=14,
            repeat_save_timing="target_turn_end",
        ),
        resource_id="spores",
    )
    template.saving_throw_actions = [spores]
    template.resources = [ResourceDefinition(id="spores", name="Spores", max_uses=1)]
    template.recharge_rules = [RechargeRule(resource_id="spores", minimum_roll=6)]
    return template


def build_ice_devil() -> CombatantTemplate:
    template = _base_template("Ice Devil", CreatureSize.LARGE, "Spear")
    wall = SavingThrowAction(
        id="srd-ice-devil-wall-of-ice",
        name="Wall of Ice",
        save_ability="dexterity",
        dc=17,
        range_ft=60,
        damage_dice_count=10,
        damage_dice_size=6,
        damage_type="cold",
        success_damage="half",
        resource_id="wall-of-ice",
    )
    template.saving_throw_actions = [wall]
    template.resources = [ResourceDefinition(id="wall-of-ice", name="Wall of Ice", max_uses=1)]
    template.recharge_rules = [RechargeRule(resource_id="wall-of-ice", minimum_roll=6)]
    return template


def build_recharge_batch() -> list[CombatantTemplate]:
    """Source-bind remaining 2014 recharge abilities.

    Rule: recharge roll >= threshold makes the ability available; otherwise nothing.
    Forced displacement (if any) ignored per locked #1032. Foundations only;
    no admission claims.
    """
    return [build_behir(), build_vrock(), build_ice_devil()]
