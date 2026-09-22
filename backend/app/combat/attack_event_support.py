from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def primary_attack_save_fields(
    save_damage: Any,
    on_hit_save: Any,
    cunning_strike_obscure: Any,
    cunning_strike: Any,
    topple: Any,
) -> tuple[Any, str | None, int | None, bool | None]:
    """Choose the primary save evidence exposed on the attack event."""
    try:
        primary = save_damage if save_damage and save_damage.save_dc is not None else on_hit_save
        if primary and primary.save_dc is not None:
            return primary.save_roll, primary.save_ability, primary.save_dc, primary.save_succeeded
        if cunning_strike_obscure and cunning_strike_obscure.save_dc is not None:
            return (
                cunning_strike_obscure.save_roll,
                "dexterity",
                cunning_strike_obscure.save_dc,
                cunning_strike_obscure.save_succeeded,
            )
        if cunning_strike and cunning_strike.save_dc is not None:
            return (
                cunning_strike.save_roll,
                "dexterity",
                cunning_strike.save_dc,
                cunning_strike.save_succeeded,
            )
        return (
            topple.save_roll if topple else None,
            "constitution" if topple and topple.save_dc is not None else None,
            topple.save_dc if topple else None,
            topple.save_succeeded if topple else None,
        )
    except Exception as exc:
        logger.exception("Failed to select primary attack save evidence.")
        raise RuntimeError("Primary attack save evidence could not be resolved.") from exc


def build_attack_description(
    *,
    attacker_name: str,
    defender_name: str,
    actual_defender_name: str,
    weapon_name: str,
    damage_type: str,
    hit: bool,
    critical: bool,
    natural_1: bool,
    natural_1_ends_turn: bool,
    heroic_reroll: bool,
    redirect_used: bool,
    parry_used: bool,
    d20_override_feature_id: str | None,
    d20_override_name: str | None,
    miss_override_feature_id: str | None,
    miss_override_name: str | None,
    damage_roll: Any,
    studied_applied: bool,
    weapon_sap_applied: bool,
    tactical_sap_applied: bool,
    vex_applied: bool,
    save_damage: Any,
    on_hit_save: Any,
    cunning_strike_obscure: Any,
    cunning_strike: Any,
    topple: Any,
    damage_outcome: str | None,
    applied_conditions: list[str],
) -> str:
    """Build player-facing attack text from already-resolved generic mechanics."""
    try:
        outcome = "CRITICAL HIT" if critical else ("HIT" if hit else "MISS")
        description = f"{attacker_name}: {outcome} with {weapon_name}."
        if d20_override_feature_id:
            description += f" {d20_override_name or d20_override_feature_id} turns the failed attack roll into a 20."
        elif miss_override_feature_id:
            description += f" {miss_override_name or miss_override_feature_id} turns the miss into a hit."
        elif natural_1_ends_turn:
            description += " Natural 1: Iron Pit immediately ends the attacker's turn."
        elif natural_1:
            description += " Natural 1: automatic miss; this off-turn attack does not terminate a future turn."
        if heroic_reroll:
            description += " Heroic Inspiration rerolls one d20."
        if not hit and damage_roll is not None:
            description += f" Graze deals {damage_roll.total} {damage_type} damage."
        if studied_applied:
            description += f" Studied Attacks primes the next attack against {defender_name}."
        if redirect_used:
            description += f" {defender_name} uses Redirect Attack; {actual_defender_name} becomes the target."
        if parry_used:
            description += f" {actual_defender_name} uses Parry."
        if weapon_sap_applied:
            description += f" Sap mastery affects {actual_defender_name}."
        if tactical_sap_applied:
            description += f" Tactical Master applies Sap to {actual_defender_name}."
        if vex_applied:
            description += f" Vex primes the next attack against {actual_defender_name}."

        for label, resolution in (
            ("", save_damage),
            ("", on_hit_save),
            ("Devious Strike Obscure", cunning_strike_obscure),
            ("Cunning Strike Trip", cunning_strike),
            ("Topple", topple),
        ):
            if resolution and resolution.save_dc is not None:
                ability = getattr(resolution, "save_ability", None)
                prefix = label or (ability.title() if ability else "")
                succeeded = "succeeds" if resolution.save_succeeded else "fails"
                description += f" {prefix} save DC {resolution.save_dc}: {actual_defender_name} {succeeded}."

        if damage_outcome == "relentless_endurance":
            description += f" {actual_defender_name} uses Relentless Endurance and remains at 1 HP."
        if damage_outcome == "undead_fortitude":
            description += f" {actual_defender_name} succeeds on Undead Fortitude and remains at 1 HP."
        labels = {
            "prone": "knocked Prone",
            "grappled": "Grappled",
            "restrained": "Restrained while Grappled",
            "poisoned": "Poisoned",
            "blinded": "Blinded",
        }
        for condition, text in labels.items():
            if condition in applied_conditions:
                description += f" {actual_defender_name} is {text}."
        return description
    except Exception as exc:
        logger.exception("Failed to build attack description for %s.", attacker_name)
        raise RuntimeError("Attack description could not be built.") from exc
