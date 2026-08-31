from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.models import (
    CombatantTemplate,
    ConditionalDamage,
    DamageType,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _source_row() -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == "Blood Hawk"]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD Blood Hawk row; found {len(rows)}.")
    return rows[0]


def build_blood_hawk() -> CombatantTemplate:
    row = _source_row()
    defenses = parse_defense_profile(row)
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError("Missing SRD Blood Hawk initiative.")
    attack = WeaponAttack(
        id="srd-blood-hawk-beak",
        weapon=Weapon(
            id="srd-blood-hawk-beak-weapon", name="Beak",
            attack_kind=WeaponAttackKind.MELEE, dice_count=1, dice_size=4,
            damage_type=DamageType.PIERCING, animation="bite", reach_ft=5,
        ),
        attack_bonus=4,
        damage_bonus=2,
        conditional_damage=[ConditionalDamage(
            trigger="target_bloodied", mode="replace_weapon",
            dice_count=1, dice_size=8, damage_bonus=2,
            damage_type=DamageType.PIERCING,
        )],
    )
    return CombatantTemplate(
        id="srd-blood-hawk", name="Blood Hawk", archetype="source-certified blood hunter",
        kind="monster", size=CreatureSize.SMALL,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)), challenge_rating=str(row["challenge"]).split()[0],
        weapon_attack=attack, combat_traits=[CombatTrait.PACK_TACTICS],
        damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
        damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
        damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
        condition_immunities=sorted(defenses["condition_immunities"]),
        visual=VisualLoadout(armor="feathers", main_hand="beak", body_style="blood-hawk"),
        source=str(row["sourceReference"]),
    )
