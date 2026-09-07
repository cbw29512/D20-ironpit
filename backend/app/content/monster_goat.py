from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.models import ChargeDamage, ChargeDefinition, CombatantTemplate, DamageType, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _source_row() -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == "Goat"]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD Goat row; found {len(rows)}.")
    return rows[0]


def build_goat() -> CombatantTemplate:
    row = _source_row()
    defenses = parse_defense_profile(row)
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError("Missing SRD Goat initiative.")
    ram = WeaponAttack(
        id="goat-ram",
        weapon=Weapon(
            id="goat-ram-weapon", name="Ram", attack_kind=WeaponAttackKind.MELEE,
            dice_count=0, dice_size=2, damage_type=DamageType.BLUDGEONING,
            animation="heavy-strike", reach_ft=5,
        ),
        attack_bonus=2, damage_bonus=0, fixed_damage=1,
        charge=ChargeDefinition(
            minimum_move_ft=20,
            replacement_damage=ChargeDamage(dice_count=1, dice_size=4, damage_type=DamageType.BLUDGEONING),
        ),
    )
    return CombatantTemplate(
        id="srd-goat", name="Goat", archetype="source-certified charging beast", kind="monster",
        size=CreatureSize(str(row["size"]).split()[0].lower()),
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)), challenge_rating=str(row["challenge"]).split()[0],
        weapon_attack=ram, combat_traits=[CombatTrait.CHARGE],
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="natural", main_hand="ram", body_style="goat"),
        source=str(row["sourceReference"]),
    )
