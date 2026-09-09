from __future__ import annotations

import logging
from typing import Any

from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def build_attack_description(
    attacker: CombatantState,
    defender: CombatantState,
    actual_defender: CombatantState,
    attack: WeaponAttack,
    *,
    hit: bool,
    critical: bool,
    natural_1: bool,
    natural_1_ends_turn: bool,
    heroic_reroll: bool,
    damage_total: int | None,
    studied_applied: bool,
    redirect_used: bool,
    parry_used: bool,
    weapon_sap_applied: bool,
    tactical_sap_applied: bool,
    vex_applied: bool,
    topple: Any,
    damage_outcome: str | None,
    applied_conditions: list[str],
) -> str:
    try:
        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        description = f"{attacker.template.name}: {outcome} with {attack.weapon.name}."
        if natural_1_ends_turn:
            description += " Natural 1: Iron Pit immediately ends the attacker's turn."
        elif natural_1:
            description += " Natural 1: automatic miss; this off-turn attack does not terminate a future turn."
        if heroic_reroll:
            description += " Heroic Inspiration rerolls one d20."
        if not hit and damage_total is not None:
            description += f" Graze deals {damage_total} {attack.weapon.damage_type.value} damage."
        if studied_applied:
            description += f" Studied Attacks primes the next attack against {defender.template.name}."
        if redirect_used:
            description += (
                f" {defender.template.name} uses Redirect Attack; "
                f"{actual_defender.template.name} becomes the target."
            )
        if parry_used:
            description += f" {actual_defender.template.name} uses Parry."
        if weapon_sap_applied:
            description += f" Sap mastery affects {actual_defender.template.name}."
        if tactical_sap_applied:
            description += f" Tactical Master applies Sap to {actual_defender.template.name}."
        if vex_applied:
            description += f" Vex primes the next attack against {actual_defender.template.name}."
        if topple and topple.save_dc is not None:
            result = "succeeds" if topple.save_succeeded else "fails"
            description += f" Topple save DC {topple.save_dc}: {actual_defender.template.name} {result}."
        if damage_outcome == "relentless_endurance":
            description += f" {actual_defender.template.name} uses Relentless Endurance and remains at 1 HP."
        if damage_outcome == "undead_fortitude":
            description += f" {actual_defender.template.name} succeeds on Undead Fortitude and remains at 1 HP."
        for condition_name, label in (
            ("prone", "is knocked Prone"),
            ("grappled", "is Grappled"),
            ("restrained", "is Restrained while Grappled"),
            ("poisoned", "is Poisoned"),
        ):
            if condition_name in applied_conditions:
                description += f" {actual_defender.template.name} {label}."
        return description
    except Exception as exc:
        logger.exception("Failed to build attack description for %s.", attacker.template.name)
        raise RuntimeError("Attack description could not be built.") from exc
