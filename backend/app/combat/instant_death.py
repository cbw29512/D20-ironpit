from __future__ import annotations

import logging

from app.combat.zero_hp_replacement import consume_instant_death_prevention
from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def apply_terminal_death(
    state: CombatantState,
    *,
    affected_states: list[CombatantState] | None = None,
) -> str:
    """Apply terminal Dead state without a prevention window."""
    try:
        if state.is_dead:
            return "unchanged"
        state.current_hp = 0
        state.is_alive = False
        state.is_dead = True
        state.is_unconscious = False
        state.is_stable = False
        state.active_effect_ids = [effect for effect in state.active_effect_ids if effect != "dodge"]
        # Terminal death uses the same form lifecycle as incapacitation in combat.
        from app.combat.replacement_form_lifecycle import revert_replacement_form_if_incapacitated
        revert_replacement_form_if_incapacitated(state)
        if state.concentration is not None:
            from app.combat.concentration import end_concentration_if_incapacitated
            end_concentration_if_incapacitated(state, affected_states)
        return "dead"
    except Exception as exc:
        logger.exception("Terminal-death resolution failed for %s.", state.template.name)
        raise RuntimeError("Terminal-death effect could not be resolved.") from exc


def apply_terminal_effect_tag(
    state: CombatantState,
    effect_tag: str,
    *,
    affected_states: list[CombatantState] | None = None,
) -> str:
    """Apply terminal death when a semantic effect tag matches target susceptibility."""
    try:
        normalized = effect_tag.strip().casefold()
        if not normalized:
            raise ValueError("Terminal effect tag must be non-empty.")
        tags = {item.strip().casefold() for item in state.template.terminal_effect_tags if item.strip()}
        if normalized not in tags:
            return "not_susceptible"
        return apply_terminal_death(state, affected_states=affected_states)
    except Exception as exc:
        logger.exception("Terminal effect-tag resolution failed for %s.", state.template.name)
        if isinstance(exc, ValueError):
            raise
        raise RuntimeError("Terminal effect-tag resolution could not be resolved.") from exc


def apply_instant_death(
    state: CombatantState,
    *,
    affected_states: list[CombatantState] | None = None,
) -> str:
    """Apply a non-damage instant-death effect, honoring source-owned prevention."""
    try:
        if state.is_dead or not state.is_alive:
            return "unchanged"
        if consume_instant_death_prevention(state):
            return "instant_death_prevented"
        return apply_terminal_death(state, affected_states=affected_states)
    except Exception as exc:
        logger.exception("Instant-death resolution failed for %s.", state.template.name)
        raise RuntimeError("Instant-death effect could not be resolved.") from exc
