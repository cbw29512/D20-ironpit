from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import (
    CombatantTemplate, ConditionalAttackAdvantage, ConditionalDamage, DamageType,
    VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
_SPECS = {
    "Giant Shark": (9, 3, 10, 6, None),
    "Hunter Shark": (6, 3, 6, 4, None),
    "Piranha": (5, 0, 2, 0, 1),
    "Reef Shark": (4, 2, 4, 2, None),
    "Swarm of Piranhas": (5, 2, 4, 3, None),
}
_CONDITIONAL_ADVANTAGE = frozenset({"Giant Shark", "Hunter Shark", "Piranha", "Swarm of Piranhas"})
_TRAITS = {"Reef Shark": [CombatTrait.PACK_TACTICS], "Swarm of Piranhas": [CombatTrait.SWARM]}


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception:
        logger.exception("Failed to slug monster name %r.", value)
        raise


def _row(name: str) -> dict[str, object]:
    try:
        matches = [row for row in load_monster_rows() if row["name"] == name]
        if len(matches) != 1:
            raise ValueError(f"Expected one SRD source row for {name!r}; found {len(matches)}.")
        return matches[0]
    except Exception:
        logger.exception("Failed to load SRD source row for %s.", name)
        raise


def _attack(name: str) -> WeaponAttack:
    try:
        bonus, count, size, damage_bonus, fixed = _SPECS[name]
        attack_id = f"srd-{_slug(name)}-{'bites' if name == 'Swarm of Piranhas' else 'bite'}"
        conditional_damage = []
        if name == "Swarm of Piranhas":
            conditional_damage = [ConditionalDamage(
                trigger="attacker_bloodied", mode="replace_weapon", dice_count=1, dice_size=4, damage_bonus=3,
                damage_type=DamageType.PIERCING,
            )]
        conditional_advantage = (
            [ConditionalAttackAdvantage(trigger="target_not_full_hp")] if name in _CONDITIONAL_ADVANTAGE else []
        )
        return WeaponAttack(
            id=attack_id,
            weapon=Weapon(
                id=f"{attack_id}-weapon", name="Bites" if name == "Swarm of Piranhas" else "Bite",
                attack_kind=WeaponAttackKind.MELEE, dice_count=count, dice_size=size,
                damage_type=DamageType.PIERCING, animation="strike", reach_ft=5,
            ),
            attack_bonus=bonus, damage_bonus=damage_bonus, fixed_damage=fixed,
            conditional_damage=conditional_damage, conditional_attack_advantage=conditional_advantage,
        )
    except Exception:
        logger.exception("Failed to build attack for %s.", name)
        raise


def _template(name: str) -> CombatantTemplate:
    try:
        row = _row(name)
        attack = _attack(name)
        defenses = parse_defense_profile(row)
        initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row["rawText"]), re.I)
        if initiative is None:
            raise ValueError(f"Missing SRD initiative for {name!r}.")
        size_name = str(row["size"]).split()[0].lower()
        multiattack = None
        if name == "Giant Shark":
            multiattack = AttackActionDefinition(
                id="srd-giant-shark-multiattack", name="Multiattack",
                slots=[AttackActionSlot(attack_ids=[attack.id]), AttackActionSlot(attack_ids=[attack.id])],
            )
        return CombatantTemplate(
            id=f"srd-{_slug(name)}", name=name, archetype="source-certified monster", kind="monster",
            size=CreatureSize(size_name), armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()),
            max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
            speed_ft=standard_arena_closing_speed(row["speed"]), movement_modes=parse_movement_profile(row["speed"]),
            initiative_bonus=int(initiative.group(1)), challenge_rating=str(row["challenge"]).split()[0],
            weapon_attack=attack, attack_action=multiattack, combat_traits=_TRAITS.get(name, []),
            damage_vulnerabilities=[DamageType(item) for item in sorted(defenses["damage_vulnerabilities"])],
            damage_resistances=[DamageType(item) for item in sorted(defenses["damage_resistances"])],
            damage_immunities=[DamageType(item) for item in sorted(defenses["damage_immunities"])],
            condition_immunities=sorted(defenses["condition_immunities"]),
            visual=VisualLoadout(armor="natural", main_hand=attack.weapon.name, body_style="monster"),
            source=str(row["sourceReference"]),
        )
    except Exception:
        logger.exception("Failed to build target-not-full-HP monster %s.", name)
        raise


def build_target_not_full_hp_monsters() -> list[CombatantTemplate]:
    try:
        return [_template(name) for name in _SPECS]
    except Exception:
        logger.exception("Failed to build target-not-full-HP monster tranche.")
        raise
