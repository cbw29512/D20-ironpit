from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, DamageType, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
_NAME = "Tough Boss"


def _source_row() -> dict[str, object]:
    try:
        matches = [row for row in load_monster_rows() if row["name"] == _NAME]
        if len(matches) != 1:
            raise ValueError(f"Expected one SRD source row for {_NAME!r}; found {len(matches)}.")
        return matches[0]
    except Exception:
        logger.exception("Failed to resolve Tough Boss SRD source row.")
        raise


def _attacks() -> list[WeaponAttack]:
    try:
        return [
            WeaponAttack(
                id="srd-tough-boss-warhammer",
                weapon=Weapon(
                    id="srd-tough-boss-warhammer-weapon", name="Warhammer",
                    attack_kind=WeaponAttackKind.MELEE, dice_count=2, dice_size=8,
                    damage_type=DamageType.BLUDGEONING, reach_ft=5, animation="strike",
                ),
                attack_bonus=5, damage_bonus=3,
                push_target_away_ft=10, push_target_max_size=CreatureSize.LARGE,
            ),
            WeaponAttack(
                id="srd-tough-boss-heavy-crossbow",
                weapon=Weapon(
                    id="srd-tough-boss-heavy-crossbow-weapon", name="Heavy Crossbow",
                    attack_kind=WeaponAttackKind.RANGED, dice_count=2, dice_size=10,
                    damage_type=DamageType.PIERCING, reach_ft=5,
                    normal_range_ft=100, long_range_ft=400, animation="strike",
                ),
                attack_bonus=4, damage_bonus=2,
            ),
        ]
    except Exception:
        logger.exception("Failed to build Tough Boss attacks.")
        raise


def build_tough_boss() -> CombatantTemplate:
    try:
        row = _source_row()
        attacks = _attacks()
        defenses = parse_defense_profile(row)
        raw = str(row["rawText"])
        initiative = re.search(r"\bInitiative\s+([+-]?\d+)", raw, re.IGNORECASE)
        if initiative is None:
            raise ValueError("Tough Boss source row is missing Initiative.")
        return CombatantTemplate(
            id="srd-tough-boss", name=_NAME, archetype="source-certified monster", kind="monster",
            size=CreatureSize.MEDIUM,
            armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
            max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
            speed_ft=standard_arena_closing_speed(row["speed"]),
            movement_modes=parse_movement_profile(row["speed"]),
            initiative_bonus=int(initiative.group(1)),
            challenge_rating=str(row["challenge"]).split()[0],
            weapon_attack=attacks[0], alternate_weapon_attacks=attacks[1:],
            attack_action=AttackActionDefinition(
                id="srd-tough-boss-multiattack", name="Multiattack",
                slots=[AttackActionSlot(attack_ids=[attack.id for attack in attacks]) for _ in range(2)],
            ),
            combat_traits=[CombatTrait.PACK_TACTICS],
            damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
            damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
            damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
            condition_immunities=sorted(defenses["condition_immunities"]),
            visual=VisualLoadout(armor="chain mail", main_hand="Warhammer", body_style="humanoid"),
            source=str(row["sourceReference"]),
        )
    except Exception:
        logger.exception("Failed to build Tough Boss runtime template.")
        raise
