from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any

from app.combat.attack_hit_damage import resolve_attack_hit_damage
from app.combat.attack_hit_riders import resolve_attack_hit_riders
from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.damage import BonusDamageSpec
from app.combat.dice import DiceProvider
from app.combat.graze import resolve_graze_miss
from app.combat.studied_attacks import apply_studied_attack_miss
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
    on_hit_maximum_hp_save: Any = None
    contested_movement: Any = None
    cunning_strike: Any = None
    cunning_strike_obscure: Any = None
    topple: Any = None
    weapon_sap_applied: bool = False
    tactical_sap_applied: bool = False
    weapon_slow_applied: bool = False
    vex_applied: bool = False
    studied_applied: bool = False
    damage_reduction_reaction_used: bool = False
    damage_reduction_reaction_source_id: str | None = None
    damage_reduction_reaction_source_name: str | None = None
    damage_reduction_reaction_reduction: int = 0
    damage_reduction_zeroed_attack: bool = False
    deferred_effect_armed: Any = None
    exile_applied: Any = None


def _copy_hit_damage(result: AttackEffectResolution, hit_damage, defender) -> None:
    result.damage_roll = hit_damage.damage_roll
    result.damage_components = hit_damage.damage_components
    result.damage_outcome = hit_damage.damage_outcome
    result.save_damage = hit_damage.save_damage
    result.damage_reduction_reaction_used = hit_damage.damage_reduction_reaction_used
    result.damage_reduction_reaction_source_id = hit_damage.damage_reduction_reaction_source_id
    result.damage_reduction_reaction_source_name = (
        defender.template.attack_damage_reduction_reaction.source_name
        if hit_damage.damage_reduction_reaction_used
        and defender.template.attack_damage_reduction_reaction is not None
        else None
    )
    result.damage_reduction_reaction_reduction = hit_damage.damage_reduction_reaction_reduction
    result.damage_reduction_zeroed_attack = hit_damage.damage_reduction_zeroed_attack
    result.cunning_strike = hit_damage.cunning_strike_trip
    result.cunning_strike_obscure = hit_damage.cunning_strike_obscure


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
    natural_roll: int | None = None,
    setup=None,
) -> AttackEffectResolution:
    """Resolve shared attack damage and generic rider composition."""
    try:
        result = AttackEffectResolution()
        if not hit:
            graze = resolve_graze_miss(attacker, defender, attack, dice, affected_states)
            if graze is not None:
                result.damage_roll, result.damage_components, result.damage_outcome = graze
                end_rage_if_incapacitated(defender)
            result.studied_applied = apply_studied_attack_miss(
                attacker, attacker_event_id, defender_event_id, round_number
            )
            return result

        active_turn_key = turn_key or f"{round_number}:{attacker_event_id}"
        hit_damage = resolve_attack_hit_damage(
            attacker,
            defender,
            attack,
            dice,
            critical,
            mode,
            active_turn_key,
            bonus_damage,
            affected_states,
            sneak_attack_ally_available,
            target_event_id=actual_event_id,
            brutal_strike_disadvantage=brutal_strike_disadvantage,
            natural_roll=natural_roll,
            setup=setup,
        )
        _copy_hit_damage(result, hit_damage, defender)
        resolve_attack_hit_riders(
            result,
            attacker,
            defender,
            attack,
            dice,
            round_number=round_number,
            attacker_event_id=attacker_event_id,
            defender_event_id=defender_event_id,
            actual_event_id=actual_event_id,
            active_turn_key=active_turn_key,
            affected_states=affected_states,
            setup=setup,
        )
        end_rage_if_incapacitated(defender)
        return result
    except Exception as exc:
        logger.exception("Failed to resolve attack effects for %s.", attacker.template.name)
        raise RuntimeError("Attack effects could not be resolved.") from exc
