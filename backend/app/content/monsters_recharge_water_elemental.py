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


def _row(name: str) -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD source row for {name!r}; found {len(rows)}.")
    return rows[0]


def build_water_elemental() -> CombatantTemplate:
    """Source-bind 2014 Water Elemental Whelm (Recharge 4-6).

    Foundation only. Forced displacement ignored per locked #1032.
    Damage and conditions on failed save remain. Does not claim admission.
    """
    row = _row("Water Elemental")
    defenses = parse_defense_profile(row)
    raw = str(row["rawText"])
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.I)
    if initiative is None:
        raise ValueError("Water Elemental source is missing Initiative.")

    whelm = SavingThrowAction(
        id="srd-water-elemental-whelm",
        name="Whelm",
        save_ability="strength",
        dc=15,
        range_ft=0,
        max_targets=20,
        damage_dice_count=2,
        damage_dice_size=8,
        damage_bonus=2,
        damage_type="bludgeoning",
        success_damage="half",
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="prone",
            expiry_timing="target_turn_end",
        ),
        resource_id="whelm",
    )
    return CombatantTemplate(
        id="srd-water-elemental",
        name="Water Elemental",
        archetype="source-certified monster",
        challenge_rating=str(row["challenge"]).split()[0],
        kind="monster",
        size=CreatureSize.LARGE,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)),
        saving_throw_actions=[whelm],
        damage_resistances=[
            DamageType(item) for item in sorted(defenses["damage_resistances"])
        ],
        damage_immunities=[
            DamageType(item) for item in sorted(defenses["damage_immunities"])
        ],
        condition_immunities=sorted(defenses["condition_immunities"]),
        resources=[ResourceDefinition(id="whelm", name="Whelm", max_uses=1)],
        recharge_rules=[RechargeRule(resource_id="whelm", minimum_roll=4)],
        visual=VisualLoadout(armor="natural", main_hand="Slam", body_style="elemental"),
        source=str(row["sourceReference"]),
    )
