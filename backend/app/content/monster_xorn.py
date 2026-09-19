from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _source_row() -> dict[str, object]:
    try:
        matches = [row for row in load_monster_rows() if row["name"] == "Xorn"]
        if len(matches) != 1:
            raise ValueError(f"Expected one SRD source row for Xorn; found {len(matches)}.")
        return matches[0]
    except Exception:
        logger.exception("Failed to load the canonical Xorn source row.")
        raise


def _attack(
    attack_id: str,
    name: str,
    dice_count: int,
    dice_size: int,
    damage_bonus: int,
    damage_type: DamageType,
) -> WeaponAttack:
    try:
        return WeaponAttack(
            id=attack_id,
            weapon=Weapon(
                id=f"{attack_id}-weapon",
                name=name,
                attack_kind=WeaponAttackKind.MELEE,
                dice_count=dice_count,
                dice_size=dice_size,
                damage_type=damage_type,
                animation="strike",
                reach_ft=5,
            ),
            attack_bonus=6,
            damage_bonus=damage_bonus,
        )
    except Exception:
        logger.exception("Failed to build Xorn attack %s.", attack_id)
        raise


def build_xorn() -> CombatantTemplate:
    """Build the 2024 SRD Xorn using existing universal movement and attack primitives."""
    try:
        row = _source_row()
        defenses = parse_defense_profile(row)
        initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.IGNORECASE)
        if initiative is None:
            raise ValueError("Xorn source row is missing Initiative.")

        bite = _attack("srd-xorn-bite", "Bite", 4, 6, 3, DamageType.PIERCING)
        claw = _attack("srd-xorn-claw", "Claw", 1, 10, 3, DamageType.SLASHING)
        multiattack = AttackActionDefinition(
            id="srd-xorn-multiattack",
            name="Multiattack",
            slots=[
                AttackActionSlot(attack_ids=[bite.id]),
                AttackActionSlot(attack_ids=[claw.id]),
                AttackActionSlot(attack_ids=[claw.id]),
                AttackActionSlot(attack_ids=[claw.id]),
            ],
        )

        return CombatantTemplate(
            id="srd-xorn",
            name="Xorn",
            archetype="source-certified monster",
            kind="monster",
            size=CreatureSize("medium"),
            armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
            max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
            speed_ft=standard_arena_closing_speed(row["speed"]),
            movement_modes=parse_movement_profile(row["speed"]),
            initiative_bonus=int(initiative.group(1)),
            challenge_rating=str(row["challenge"]).split()[0],
            weapon_attack=bite,
            alternate_weapon_attacks=[claw],
            attack_action=multiattack,
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
            visual=VisualLoadout(
                armor="natural",
                main_hand="Bite",
                body_style="monster",
            ),
            source=str(row["sourceReference"]),
        )
    except Exception:
        logger.exception("Failed to build the source-certified Xorn.")
        raise
