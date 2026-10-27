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


def build_giant_spider() -> CombatantTemplate:
    """Source-bind 2014 Giant Spider Web (Recharge 5-6).

    Foundation only. Does not claim admission. Remaining attack:incomplete
    and attack:damage-type blockers stay until full Bite/Poison parity.
    """
    row = _row("Giant Spider")
    defenses = parse_defense_profile(row)
    raw = str(row["rawText"])
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.I)
    if initiative is None:
        raise ValueError("Giant Spider source is missing Initiative.")

    web = SavingThrowAction(
        id="srd-giant-spider-web",
        name="Web",
        save_ability="dexterity",
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
    return CombatantTemplate(
        id="srd-giant-spider",
        name="Giant Spider",
        archetype="source-certified monster",
        challenge_rating=str(row["challenge"]).split()[0],
        kind="monster",
        size=CreatureSize.LARGE,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)),
        saving_throw_actions=[web],
        damage_resistances=[
            DamageType(item) for item in sorted(defenses["damage_resistances"])
        ],
        damage_immunities=[
            DamageType(item) for item in sorted(defenses["damage_immunities"])
        ],
        condition_immunities=sorted(defenses["condition_immunities"]),
        resources=[ResourceDefinition(id="web", name="Web", max_uses=1)],
        recharge_rules=[RechargeRule(resource_id="web", minimum_roll=5)],
        visual=VisualLoadout(armor="natural", main_hand="Bite", body_style="spider"),
        source=str(row["sourceReference"]),
    )
