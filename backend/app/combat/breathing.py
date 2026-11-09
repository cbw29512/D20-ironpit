"""2014 universal held-breath and suffocation lifecycle (source-neutral)."""
from __future__ import annotations

import logging

from app.combat.zero_hp import reduce_to_zero_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)


def unable_to_breathe(state: CombatantState) -> bool:
    """The source's active Grapple, not creature identity, blocks respiration."""
    try:
        return state.template.needs_air and any(
            source.prevents_breathing for source in state.grapple_sources
        )
    except Exception:
        logger.exception("Failed breathing eligibility for %s.", state.template.name)
        raise


def reset_breathing(state: CombatantState) -> None:
    try:
        state.breath_hold_rounds_remaining = None
        state.breath_survival_rounds_remaining = None
        state.suffocating_at_zero = False
    except Exception:
        logger.exception("Failed breathing reset for %s.", state.template.name)
        raise


def suffocation_blocks_recovery(state: CombatantState) -> bool:
    """2014 recovery lock begins only after air deprivation causes 0 HP."""
    try:
        return bool(state.suffocating_at_zero and unable_to_breathe(state))
    except Exception:
        logger.exception("Failed suffocation recovery check for %s.", state.template.name)
        raise


def _budget(state: CombatantState) -> tuple[int, int]:
    scores = state.template.ability_scores
    if scores is None:
        raise ValueError(f"{state.template.name}: suffocation requires a Constitution score.")
    constitution_modifier = scores.modifier("constitution")
    hold = state.template.breath_hold_rounds
    if hold is None:
        hold = max(5, (1 + constitution_modifier) * 10)
    return hold, max(1, constitution_modifier)


def _source_name(state: CombatantState, setup: EncounterSetup) -> str:
    source = next(item for item in state.grapple_sources if item.prevents_breathing)
    for owner in [*setup.heroes, *setup.monsters]:
        if owner.combatant_id != source.source_id:
            continue
        for action in owner.state.template.saving_throw_actions:
            if action.id == source.linked_effect_id:
                return action.name
    return source.linked_effect_id or "Grapple"


def resolve_breathing_start_turn(
    sequence: int, round_number: int, member: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """Advance one affected creature turn; release immediately resets the clock."""
    state = member.state
    try:
        if not unable_to_breathe(state):
            reset_breathing(state)
            return [], sequence
        if state.template.ruleset != "2014":
            raise ValueError("2024 suffocation requires its distinct exhaustion lifecycle.")
        if state.is_dead or state.suffocating_at_zero:
            return [], sequence
        if state.breath_hold_rounds_remaining is None:
            hold, survival = _budget(state)
            state.breath_hold_rounds_remaining = hold
            state.breath_survival_rounds_remaining = survival
        if state.breath_hold_rounds_remaining > 0:
            state.breath_hold_rounds_remaining -= 1
            if state.breath_hold_rounds_remaining > 0:
                return [], sequence
            description = (
                f"{state.template.name} exhausts held breath while caught in "
                f"{_source_name(state, setup)}."
            )
        elif state.breath_survival_rounds_remaining > 0:
            state.breath_survival_rounds_remaining -= 1
            return [], sequence
        else:
            before = state.current_hp
            outcome = reduce_to_zero_hit_points(
                state, affected_states=[m.state for m in [*setup.heroes, *setup.monsters]],
            )
            # The rule also ends Stable for a creature already unconscious at 0 HP.
            if state.current_hp == 0 and not state.is_dead:
                state.is_stable = False
                state.is_unconscious = True
                state.suffocating_at_zero = True
            description = (
                f"{state.template.name} suffocates under {_source_name(state, setup)}: "
                f"{before} to {state.current_hp} HP ({outcome})."
            )
        event = BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=member.combatant_id, actor_name=state.template.name,
            target_id=member.combatant_id, target_name=state.template.name,
            feature_id="suffocation", animation="condition",
            description=description, hp_after=state.current_hp,
        )
        return [event], sequence + 1
    except Exception:
        logger.exception(
            "Failed 2014 breathing turn for %s, round %s.", state.template.name, round_number,
        )
        raise
