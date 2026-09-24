from __future__ import annotations

import logging
from typing import Literal

from app.combat.concentration import resolve_concentration_damage
from app.combat.dice import DiceProvider
from app.combat.hit_points import effective_max_hp
from app.combat.orc import use_relentless_endurance
from app.combat.source_bound_effects import end_damage_sensitive_effects
from app.combat.survival_wards import consume_survival_ward
from app.combat.undead_fortitude import resolve_undead_fortitude, resolve_effect_bound_survival_save
from app.combat.zero_hp_state import damage_at_zero, mark_dead, mark_unconscious, reset_death_saves
from app.combat.hit_point_recovery import restore_hit_points
from app.domain.models import CombatantState, DamageType

logger = logging.getLogger(__name__)
ZeroHpOutcome = Literal[
    "damaged", "unconscious", "dead", "unchanged", "relentless_endurance", "undead_fortitude", "survival_save", "survival_ward",
]
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
        if consume_survival_ward(state):
            outcome = "survival_ward"
        elif state.template.kind == "monster":
            outcome = mark_dead(state)
        elif resolve_effect_bound_survival_save(state, dice):
            outcome = "survival_save"
        elif use_relentless_endurance(state, 0):
            outcome = "relentless_endurance"
        else:
            outcome = mark_unconscious(state)
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
) -> ZeroHpOutcome:
    """Apply Temporary HP, Concentration, and SRD 5.2.1 zero-HP lifecycle rules."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        if amount == 0 or state.is_dead:
            return "unchanged"

        incoming = amount
        types = damage_types or set()
        amount = _after_temporary_hp(state, amount)
        if state.current_hp == 0:
            return _finish_damage(state, damage_at_zero(state, incoming, critical=critical), incoming, dice, affected_states)
        if amount == 0:
            return _finish_damage(state, "damaged", incoming, dice, affected_states)

        hp_before = state.current_hp
        state.current_hp = max(0, hp_before - amount)
        if state.current_hp > 0:
            return _finish_damage(state, "damaged", incoming, dice, affected_states)
        if consume_survival_ward(state):
            return _finish_damage(state, "survival_ward", incoming, dice, affected_states)
        if resolve_undead_fortitude(
            state, incoming, types, critical=critical, dice=dice,
        ):
            return _finish_damage(state, "undead_fortitude", incoming, dice, affected_states)
        if state.template.kind == "monster":
            return _finish_damage(state, mark_dead(state), incoming, dice, affected_states)

        remaining_damage = max(0, amount - hp_before)
        if remaining_damage >= effective_max_hp(state):
            return _finish_damage(state, mark_dead(state), incoming, dice, affected_states)
        if resolve_effect_bound_survival_save(state, dice):
            return _finish_damage(state, "survival_save", incoming, dice, affected_states)
        if use_relentless_endurance(state, remaining_damage):
            return _finish_damage(state, "relentless_endurance", incoming, dice, affected_states)
        return _finish_damage(state, mark_unconscious(state), incoming, dice, affected_states)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Zero-HP damage resolution failed for %s.", state.template.name)
        raise RuntimeError("Zero-HP damage could not be resolved.") from exc


def apply_instant_death(
    state: CombatantState,
    *,
    affected_states: list[CombatantState] | None = None,
) -> ZeroHpOutcome:
    """Resolve an effect that kills without dealing damage."""
    try:
        if state.is_dead:
            return "unchanged"
        if consume_survival_ward(state, nondamage_instant_death=True):
            return "survival_ward"
        outcome = mark_dead(state)
        if state.concentration is not None:
            from app.combat.concentration import end_concentration_if_incapacitated
            end_concentration_if_incapacitated(state, affected_states)
        return outcome
    except Exception as exc:
        logger.exception("Instant-death resolution failed for %s.", state.template.name)
        raise RuntimeError("Instant-death effect could not be resolved.") from exc
