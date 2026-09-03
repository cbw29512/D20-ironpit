from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.models import CombatantTemplate, DamageType, OnHitDamage, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize


def _source_row() -> dict[str, object]:
    rows = [row for row in load_monster_rows() if row["name"] == "Merfolk Skirmisher"]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD Merfolk Skirmisher row; found {len(rows)}.")
    return rows[0]


def _ocean_spear(attack_id: str, kind: WeaponAttackKind) -> WeaponAttack:
    ranged = kind is WeaponAttackKind.RANGED
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=f"{attack_id}-weapon", name="Ocean Spear", attack_kind=kind,
            dice_count=1, dice_size=6, damage_type=DamageType.PIERCING,
            animation="projectile" if ranged else "thrust", reach_ft=5,
            normal_range_ft=20 if ranged else None,
            long_range_ft=60 if ranged else None,
            projectile="spear" if ranged else None,
        ),
        attack_bonus=2, damage_bonus=0,
        on_hit_damage=[OnHitDamage(
            source="Cold", dice_count=1, dice_size=4, damage_type=DamageType.COLD,
        )],
        on_hit_modifier_effects=[HitModifierEffect(
            kind="speed", flat_bonus=-10, expires_at_end_of_target_turn=True,
        )],
    )


def build_merfolk_skirmisher() -> CombatantTemplate:
    row = _source_row()
    initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
    if initiative is None:
        raise ValueError("Missing SRD Merfolk Skirmisher initiative.")
    return CombatantTemplate(
        id="srd-merfolk-skirmisher", name="Merfolk Skirmisher",
        archetype="source-certified aquatic skirmisher", kind="monster", creature_type="elemental",
        size=CreatureSize.MEDIUM,
        armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
        max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
        speed_ft=standard_arena_closing_speed(row["speed"]),
        movement_modes=parse_movement_profile(row["speed"]),
        initiative_bonus=int(initiative.group(1)), challenge_rating=str(row["challenge"]).split()[0],
        weapon_attack=_ocean_spear("merfolk-skirmisher-ocean-spear-ranged", WeaponAttackKind.RANGED),
        alternate_weapon_attacks=[_ocean_spear("merfolk-skirmisher-ocean-spear-melee", WeaponAttackKind.MELEE)],
        visual=VisualLoadout(armor="natural", main_hand="spear", body_style="merfolk-skirmisher"),
        source=str(row["sourceReference"]),
    )
