from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import end_concentration, start_concentration
from app.combat.condition_rules import has_condition
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState

logger = logging.getLogger(__name__)
INVISIBLE_EFFECT_ID = "invisible"


def _states(setup: EncounterSetup | None) -> list[CombatantState]:
    if setup is None:
        return []
    return [member.state for member in [*setup.heroes, *setup.monsters]]


def can_use_invisibility(state: CombatantState) -> bool:
    try:
        return (
            state.template.invisibility_action is not None
            and is_available(state, state.template.invisibility_action.action_cost)
            and not has_condition(state, INVISIBLE_EFFECT_ID)
        )
    except Exception:
        logger.exception("Failed to evaluate invisibility legality for %s.", state.template.name)
        raise


def resolve_invisibility_action(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> BattleEvent:
    try:
        profile = actor.state.template.invisibility_action
        if profile is None or not can_use_invisibility(actor.state):
            raise ValueError("Invisibility action is not legal.")
        affected = _states(setup)
        if profile.concentration:
            start_concentration(
                actor.state,
                actor.combatant_id,
                profile.id,
                round_number,
                affected_states=affected,
            )
        applied = apply_timed_condition(
            actor.state,
            INVISIBLE_EFFECT_ID,
            actor.combatant_id,
            source_effect_id=profile.id,
            applied_round=round_number,
            expires_at_start_of_source_turn=False,
            affected_states=affected,
        )
        if applied is None:
            raise ValueError("Invisibility could not be applied.")
        spend(actor.state, profile.action_cost)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=actor.combatant_id,
            target_name=actor.state.template.name,
            applied_condition_ids=[INVISIBLE_EFFECT_ID],
            feature_id=profile.id,
            concentration_started_effect_id=profile.id if profile.concentration else None,
            animation="invisibility",
            description=f"{actor.state.template.name} uses {profile.name} and becomes Invisible.",
        )
    except Exception as exc:
        logger.exception("Invisibility action failed for %s.", actor.combatant_id)
        raise RuntimeError("Invisibility action could not be resolved.") from exc


def end_attack_invisibility(
    state: CombatantState,
    affected_states: list[CombatantState] | None = None,
) -> bool:
    try:
        profile = state.template.invisibility_action
        if profile is None or not profile.ends_on_attack or not has_condition(state, INVISIBLE_EFFECT_ID):
            return False
        owns_effect = any(
            effect.effect_id == INVISIBLE_EFFECT_ID and effect.source_effect_id == profile.id
            for effect in state.timed_effects
        )
        if not owns_effect:
            return False
        if state.concentration is not None and state.concentration.effect_id == profile.id:
            return end_concentration(state, affected_states)
        state.timed_effects = [
            effect for effect in state.timed_effects
            if not (effect.effect_id == INVISIBLE_EFFECT_ID and effect.source_effect_id == profile.id)
        ]
        if not any(effect.effect_id == INVISIBLE_EFFECT_ID for effect in state.timed_effects):
            state.active_effect_ids = [item for item in state.active_effect_ids if item != INVISIBLE_EFFECT_ID]
        return True
    except Exception:
        logger.exception("Failed to end attack-triggered invisibility for %s.", state.template.name)
        raise
