from __future__ import annotations

import logging
from typing import Literal
from app.combat.turn_damage import note_turn_damage
from app.combat.damage_taken_effects import apply_damage_taken_timed_effects
from app.combat.concentration import resolve_concentration_damage
from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.hit_points import effective_max_hp
from app.combat.orc import use_relentless_endurance
from app.combat.replacement_form_lifecycle import apply_replacement_form_damage, revert_replacement_form_if_incapacitated
from app.combat.source_bound_effects import end_damage_sensitive_effects
from app.combat.regeneration_lifecycle import delay_zero_hp_death, note_incoming_damage_types
from app.combat.undead_fortitude import resolve_undead_fortitude, resolve_effect_bound_survival_save
from app.combat.zero_hp_replacement import consume_damage_threshold_zero_hp_replacement, consume_zero_hp_replacement
from app.domain.models import CombatantState, DamageRollComponent, DamageType
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
ZeroHpOutcome = Literal[
    "damaged", "unconscious", "dead", "unchanged", "relentless_endurance", "undead_fortitude",
    "survival_save", "zero_hp_replacement", "damage_threshold_zero_hp_replacement",
]
DODGE_EFFECT_ID = "dodge"
PRONE_EFFECT_ID = "prone"

def reset_death_saves(state: CombatantState) -> None:
    state.death_save_successes = 0
    state.death_save_failures = 0


def _mark_dead(state: CombatantState) -> ZeroHpOutcome:
    if delay_zero_hp_death(state):
        return _mark_unconscious(state)
    state.current_hp = 0
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False
    state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != DODGE_EFFECT_ID]
    revert_replacement_form_if_incapacitated(state)
    return "dead"


def _mark_unconscious(state: CombatantState) -> ZeroHpOutcome:
    state.is_alive = True
    state.is_unconscious = True
    state.is_stable = False
    state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != DODGE_EFFECT_ID]
    if not condition_is_immune(state, PRONE_EFFECT_ID) and PRONE_EFFECT_ID not in state.active_effect_ids:
        state.active_effect_ids.append(PRONE_EFFECT_ID)
    revert_replacement_form_if_incapacitated(state)
    return "unconscious"


def _after_temporary_hp(state: CombatantState, amount: int) -> int:
    absorbed = min(state.temporary_hp, amount)
    state.temporary_hp -= absorbed
    return amount - absorbed


def _finish_damage(
    state: CombatantState,
    outcome: ZeroHpOutcome,
    damage_taken: int,
    dice: DiceProvider | None,
    affected_states: list[CombatantState] | None,
) -> ZeroHpOutcome:
    end_damage_sensitive_effects(state)
    if state.concentration is None:
        return outcome
    if dice is None:
        if state.is_dead or state.is_unconscious:
            from app.combat.concentration import end_concentration_if_incapacitated
            end_concentration_if_incapacitated(state, affected_states)
            return outcome
        raise ValueError("A dice provider is required to resolve Concentration damage.")
    resolve_concentration_damage(state, damage_taken, dice, affected_states)
    return outcome


def restore_hit_points(state: CombatantState, amount: int) -> int:
    """Restore true HP; ordinary healing cannot restore a dead creature or a Swarm."""
    if amount < 0:
        raise ValueError("Healing cannot be negative.")
    if state.is_dead or amount == 0 or CombatTrait.SWARM in state.template.combat_traits:
        return 0
    before = state.current_hp
    state.current_hp = min(effective_max_hp(state), before + amount)
    healed = state.current_hp - before
    if healed > 0:
        state.is_alive = True
        state.is_unconscious = False
        state.is_stable = False
        reset_death_saves(state)
    return healed


def _damage_at_zero(state: CombatantState, incoming: int, *, critical: bool) -> ZeroHpOutcome:
    if state.template.kind == "monster" or incoming >= effective_max_hp(state):
        return _mark_dead(state)
    state.is_stable = False
    state.death_save_failures = min(3, state.death_save_failures + (2 if critical else 1))
    if state.death_save_failures >= 3:
        return _mark_dead(state)
    return _mark_unconscious(state)


def reduce_to_zero_hit_points(
    state: CombatantState,
    *,
    dice: DiceProvider | None = None,
    affected_states: list[CombatantState] | None = None,
) -> ZeroHpOutcome:
    """Set true HP to zero without treating the effect as damage."""
    try:
        if state.is_dead or state.current_hp == 0:
            return "unchanged"
        state.current_hp = 0
        if state.template.kind == "monster":
            outcome = _mark_dead(state)
        elif resolve_effect_bound_survival_save(state, dice):
            outcome = "survival_save"
        elif use_relentless_endurance(state, 0):
            outcome = "relentless_endurance"
        else:
            outcome = _mark_unconscious(state)
        if state.is_dead or state.is_unconscious:
            from app.combat.concentration import end_concentration_if_incapacitated
            end_concentration_if_incapacitated(state, affected_states)
        return outcome
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Zero-HP reduction failed for %s.", state.template.name)
        raise RuntimeError("Zero-HP reduction could not be resolved.") from exc


def apply_damage(
    state: CombatantState,
    amount: int,
    *,
    critical: bool = False,
    damage_types: set[DamageType] | None = None,
    dice: DiceProvider | None = None,
    affected_states: list[CombatantState] | None = None,
    setup=None,
    damage_components: list[DamageRollComponent] | None = None,
) -> ZeroHpOutcome:
    """Apply Temporary HP, Concentration, and SRD 5.2.1 zero-HP lifecycle rules."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        if amount == 0 or state.is_dead:
            return "unchanged"

        incoming = amount
        types = damage_types or set()
        note_incoming_damage_types(state, types)
        damage_before = dict(state.damage_taken_this_turn_by_type)
        note_turn_damage(state, incoming, types, damage_components)
        apply_damage_taken_timed_effects(state, damage_before)
        amount = _after_temporary_hp(state, amount)
        amount, _ = apply_replacement_form_damage(state, amount)
        if state.current_hp == 0:
            outcome = _finish_damage(state, _damage_at_zero(state, incoming, critical=critical), incoming, dice, affected_states)
        elif amount == 0:
            outcome = _finish_damage(state, "damaged", incoming, dice, affected_states)
        else:
            hp_before = state.current_hp
            state.current_hp = max(0, hp_before - amount)
            if state.current_hp > 0:
                outcome = _finish_damage(state, "damaged", incoming, dice, affected_states)
            elif consume_damage_threshold_zero_hp_replacement(state, incoming):
                outcome = _finish_damage(state, "damage_threshold_zero_hp_replacement", incoming, dice, affected_states)
            elif consume_zero_hp_replacement(state):
                outcome = _finish_damage(state, "zero_hp_replacement", incoming, dice, affected_states)
            elif resolve_undead_fortitude(state, incoming, types, critical=critical, dice=dice):
                outcome = _finish_damage(state, "undead_fortitude", incoming, dice, affected_states)
            elif state.template.kind == "monster":
                outcome = _finish_damage(state, _mark_dead(state), incoming, dice, affected_states)
            else:
                remaining_damage = max(0, amount - hp_before)
                if remaining_damage >= effective_max_hp(state):
                    outcome = _finish_damage(state, _mark_dead(state), incoming, dice, affected_states)
                elif resolve_effect_bound_survival_save(state, dice):
                    outcome = _finish_damage(state, "survival_save", incoming, dice, affected_states)
                elif use_relentless_endurance(state, remaining_damage):
                    outcome = _finish_damage(state, "relentless_endurance", incoming, dice, affected_states)
                else:
                    outcome = _finish_damage(state, _mark_unconscious(state), incoming, dice, affected_states)
        if incoming > 0 and state.damage_share_source_id:
            if setup is None:
                raise ValueError("Damage share requires encounter setup.")
            from app.combat.damage_share import resolve_damage_share_for_state
            resolve_damage_share_for_state(state, incoming, setup, dice)
        return outcome
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Zero-HP damage resolution failed for %s.", state.template.name)
        raise RuntimeError("Zero-HP damage could not be resolved.") from exc
