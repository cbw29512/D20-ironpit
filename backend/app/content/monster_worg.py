from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.models import CombatantTemplate, DamageType, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize


def _source_row() -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == "Worg"]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD Worg row; found {len(rows)}.")
    return rows[0]


def build_worg() -> CombatantTemplate:
    row = _source_row()
    defenses = parse_defense_profile(row)
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError("Missing SRD Worg initiative.")
    bite = WeaponAttack(
        id="srd-worg-bite",
        weapon=Weapon(
            id="srd-worg-bite-weapon", name="Bite", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=8, damage_type=DamageType.PIERCING, animation="bite", reach_ft=5,
        ),
        attack_bonus=5, damage_bonus=3,
        on_hit_modifier_effects=[HitModifierEffect(
            kind="attacks-against-advantage", consume_on_attack_against=True,
            expires_at_start_of_source_turn=True,
        )],
    )
    return CombatantTemplate(
        id="srd-worg", name="Worg", archetype="source-certified pack predator", kind="monster",
        size=CreatureSize.LARGE,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)), challenge_rating=str(row["challenge"]).split()[0],
        skill_bonuses={"perception": 4}, weapon_attack=bite,
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="fur", main_hand="bite", body_style="worg"),
        source=str(row["sourceReference"]),
    )
