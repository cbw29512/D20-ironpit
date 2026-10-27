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


def build_dust_mephit() -> CombatantTemplate:
    template = _base_template("Dust Mephit", CreatureSize.SMALL, "Claws")
    breath = SavingThrowAction(
        id="srd-dust-mephit-blinding-breath",
        name="Blinding Breath",
        save_ability="dexterity",
        dc=10,
        range_ft=15,
        area=AreaTargeting(shape="cone", origin="self", length_ft=15),
        damage_dice_count=0,
        success_damage="none",
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="blinded",
            duration_rounds=10,
            expiry_timing="target_turn_end",
            repeat_save_ability="dexterity",
            repeat_save_dc=10,
            repeat_save_timing="target_turn_end",
        ),
        resource_id="blinding-breath",
    )
    template.saving_throw_actions = [breath]
    template.resources = [ResourceDefinition(id="blinding-breath", name="Blinding Breath", max_uses=1)]
    template.recharge_rules = [RechargeRule(resource_id="blinding-breath", minimum_roll=6)]
    return template


def build_ettercap() -> CombatantTemplate:
    template = _base_template("Ettercap", CreatureSize.MEDIUM, "Claws")
    web = SavingThrowAction(
        id="srd-ettercap-web",
        name="Web",
        save_ability="strength",
        dc=11,
        range_ft=30,
        max_targets=1,
        damage_dice_count=0,
        success_damage="none",
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="restrained",
            expiry_timing="target_turn_end",
        ),
        resource_id="web",
    )
    template.saving_throw_actions = [web]
    template.resources = [ResourceDefinition(id="web", name="Web", max_uses=1)]
    template.recharge_rules = [RechargeRule(resource_id="web", minimum_roll=5)]
    return template


def build_ghost() -> CombatantTemplate:
    template = _base_template("Ghost", CreatureSize.MEDIUM, "Withering Touch")
    possession = SavingThrowAction(
        id="srd-ghost-possession",
        name="Possession",
        save_ability="charisma",
        dc=13,
        range_ft=5,
        max_targets=1,
        damage_dice_count=0,
        success_damage="none",
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="incapacitated",
            expiry_timing="target_turn_end",
        ),
        resource_id="possession",
    )
    template.saving_throw_actions = [possession]
    template.resources = [ResourceDefinition(id="possession", name="Possession", max_uses=1)]
    template.recharge_rules = [RechargeRule(resource_id="possession", minimum_roll=6)]
    return template


def build_recharge_batch_2() -> list[CombatantTemplate]:
    """Source-bind remaining 2014 recharge abilities.

    Rule: recharge roll >= threshold makes the ability available; otherwise nothing.
    Foundations only; no admission claims.
    """
    return [build_dust_mephit(), build_ettercap(), build_ghost()]
