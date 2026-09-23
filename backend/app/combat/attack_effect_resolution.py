from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any

from app.combat.attack_hit_damage import resolve_attack_hit_damage
from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.conditions import apply_hit_conditions
from app.combat.damage import BonusDamageSpec
from app.combat.deferred_save_effect import arm_deferred_save_effect
from app.combat.dice import DiceProvider
from app.combat.graze import resolve_graze_miss
from app.combat.on_hit_condition_save import resolve_on_hit_condition_save
from app.combat.sap import apply_weapon_sap
from app.combat.studied_attacks import apply_studied_attack_miss
from app.combat.tactical_master import apply_tactical_master_sap
from app.combat.topple import resolve_topple_hit
from app.combat.vex import apply_vex_mastery
from app.domain.models import CombatantState, RollMode, WeaponAttack

logger = logging.getLogger(__name__)


@dataclass
class AttackEffectResolution:
    damage_roll: Any = None
    damage_components: list[Any] = field(default_factory=list)
    damage_outcome: str | None = None
    applied_conditions: list[str] = field(default_factory=list)
    save_damage: Any = None
    on_hit_save: Any = None
    cunning_strike: Any = None
    cunning_strike_obscure: Any = None
    topple: Any = None
    weapon_sap_applied: bool = False
    tactical_sap_applied: bool = False
    vex_applied: bool = False
    studied_applied: bool = False
    deferred_effect_armed: Any = None


def resolve_attack_effects(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    *,
    hit: bool,
    critical: bool,
    mode: RollMode,
    round_number: int,
    attacker_event_id: str,
    defender_event_id: str,
    actual_event_id: str,
    turn_key: str | None,
    bonus_damage: BonusDamageSpec | None,
    affected_states: list[CombatantState] | None,
    sneak_attack_ally_available: bool,
    brutal_strike_disadvantage: int,
) -> AttackEffectResolution:
    """Resolve shared on-hit/on-miss effects after the final attack outcome is known."""
    try:
        result = AttackEffectResolution()
        if not hit:
            graze = resolve_graze_miss(attacker, defender, attack, dice, affected_states)
            if graze is not None:
                result.damage_roll, result.damage_components, result.damage_outcome = graze
                end_rage_if_incapacitated(defender)
            result.studied_applied = apply_studied_attack_miss(
                attacker, attacker_event_id, defender_event_id, round_number,
            )
            return result

        active_turn_key = turn_key or f"{round_number}:{attacker_event_id}"
        hit_damage = resolve_attack_hit_damage(
            attacker, defender, attack, dice, critical, mode, active_turn_key,
            bonus_damage, affected_states, sneak_attack_ally_available,
            brutal_strike_disadvantage=brutal_strike_disadvantage,
        )
        result.damage_roll = hit_damage.damage_roll
        result.damage_components = hit_damage.damage_components
        result.damage_outcome = hit_damage.damage_outcome
        result.save_damage = hit_damage.save_damage
        result.cunning_strike = hit_damage.cunning_strike_trip
        result.cunning_strike_obscure = hit_damage.cunning_strike_obscure
        if result.cunning_strike.applied:
            result.applied_conditions.append("prone")
        if result.cunning_strike_obscure.applied:
            result.applied_conditions.append("blinded")
        result.applied_conditions.extend(
            apply_hit_conditions(
                attack, defender, attacker_event_id, round_number,
                affected_states, attacker.template,
            )
        )
        result.on_hit_save = resolve_on_hit_condition_save(
            defender, attack, dice, attacker.template,
        )
        if (
            result.on_hit_save.applied_condition
            and result.on_hit_save.applied_condition not in result.applied_conditions
        ):
            result.applied_conditions.append(result.on_hit_save.applied_condition)
        result.topple = resolve_topple_hit(attacker, defender, attack, dice)
        if result.topple.applied and "prone" not in result.applied_conditions:
            result.applied_conditions.append("prone")
        result.weapon_sap_applied = apply_weapon_sap(
            attacker, attacker_event_id, defender, attack, round_number,
        )
        if not result.weapon_sap_applied:
            result.tactical_sap_applied = apply_tactical_master_sap(
                attacker, attacker_event_id, defender, attack, round_number,
            )
        applied_total = sum(
            component.applied_total or 0 for component in result.damage_components
        )
        result.vex_applied = apply_vex_mastery(
            attacker, attacker_event_id, actual_event_id, attack, round_number, applied_total,
        )
        result.deferred_effect_armed = arm_deferred_save_effect(
            attacker, defender, actual_event_id, attack, round_number,
        )
        end_rage_if_incapacitated(defender)
        return result
    except Exception as exc:
        logger.exception("Failed to resolve attack effects for %s.", attacker.template.name)
        raise RuntimeError("Attack effects could not be resolved.") from exc
