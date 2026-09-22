from __future__ import annotations

import logging

from app.combat.d20_outcome_adjustments import adjust_d20_outcome
from app.combat.defensive_modifier_rules import death_save_advantage_sources
from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.combat.zero_hp import restore_hit_points, reset_death_saves
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, RollMode

logger = logging.getLogger(__name__)


def _mark_dead(state: CombatantState) -> None:
    state.is_alive = False
    state.is_dead = True
    state.is_unconscious = False
    state.is_stable = False


def resolve_death_save(
    sequence: int,
    round_number: int,
    combatant_id: str,
    state: CombatantState,
    dice: DiceProvider,
    *, roller: EncounterCombatant | None = None, setup: EncounterSetup | None = None,
) -> BattleEvent:
    """Resolve one SRD 5.2.1 Death Saving Throw at the start of a character turn."""
    try:
        if state.template.kind != "character":
            raise ValueError("Only player characters make Death Saving Throws by default.")
        if state.current_hp != 0 or state.is_dead or state.is_stable:
            raise ValueError("This character does not currently make a Death Saving Throw.")

        features = state.template.progression_features
        advantage = features.death_save_advantage or bool(death_save_advantage_sources(state))
        mode = RollMode.ADVANTAGE if advantage else RollMode.NORMAL
        roll = roll_d20(dice, 0, mode)
        natural = roll.selected_roll or 0
        recovery_minimum = features.death_save_recovery_minimum
        hp_before = state.current_hp
        successes_before = state.death_save_successes
        failures_before = state.death_save_failures
        result = "failure"

        if natural >= recovery_minimum:
            restore_hit_points(state, 1)
            result = f"{natural} triggers death-save recovery; regains 1 HP"
        elif natural == 1:
            state.death_save_failures = min(3, state.death_save_failures + 2)
            result = "natural 1; two failures"
        else:
            succeeded = roll.total >= 10
            if roller is not None:
                roll, succeeded, _ = adjust_d20_outcome(roll, succeeded, 10, roller, setup, dice)
            if succeeded:
                state.death_save_successes = min(3, state.death_save_successes + 1)
                result = "success"
            else:
                state.death_save_failures = min(3, state.death_save_failures + 1)

        if state.death_save_failures >= 3:
            _mark_dead(state)
            result = "third failure; dies"
        elif state.death_save_successes >= 3:
            state.is_stable = True
            state.is_unconscious = True
            reset_death_saves(state)
            result = "third success; becomes Stable"

        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="death_save",
            actor_id=combatant_id, actor_name=state.template.name,
            target_id=combatant_id, target_name=state.template.name, death_save_roll=roll,
            hp_before=hp_before, hp_after=state.current_hp,
            death_save_successes_before=successes_before, death_save_failures_before=failures_before,
            death_save_successes=state.death_save_successes, death_save_failures=state.death_save_failures,
            is_stable=state.is_stable, is_dead=state.is_dead, animation="death-save",
            description=f"{state.template.name} makes a Death Save: {result}.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Death Save failed for %s.", state.template.name)
        raise RuntimeError("Death Saving Throw could not be resolved.") from exc
