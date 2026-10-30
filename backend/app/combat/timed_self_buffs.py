from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import start_concentration
from app.combat.resources import resource_state
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def timed_self_buff_active(member: EncounterCombatant, action: TimedSelfBuffAction) -> bool:
    try:
        return any(effect.source_effect_id == action.id for effect in member.state.timed_effects)
    except Exception as exc:
        logger.exception("Failed timed self-buff active check for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff state could not be inspected.") from exc


def choose_timed_self_buff(
    member: EncounterCombatant,
    action_cost: str,
) -> TimedSelfBuffAction | None:
    try:
        if not is_available(member.state, action_cost):
            return None
        actions = sorted(
            (
                action for action in member.state.template.timed_self_buff_actions
                if action.action_cost == action_cost
            ),
            key=lambda action: -action.priority,
        )
        for action in actions:
            if timed_self_buff_active(member, action):
                continue
            if action.concentration and member.state.concentration is not None:
                continue
            if action.resource_id is not None:
                try:
                    resource = resource_state(member.state, action.resource_id)
                except ValueError:
                    continue
                if resource.current_uses < action.resource_cost:
                    continue
            return action
        return None
    except Exception as exc:
        logger.exception("Failed timed self-buff selection for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff selection failed.") from exc


def resolve_timed_self_buff(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
    affected_states: list | None = None,
) -> BattleEvent:
    try:
        if not is_available(member.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if timed_self_buff_active(member, action):
            raise ValueError(f"{action.name} is already active.")
        resource = None
        if action.resource_id is not None:
            resource = resource_state(member.state, action.resource_id)
            if resource.current_uses < action.resource_cost:
                raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        spend(member.state, action.action_cost)
        if resource is not None:
            resource.current_uses -= action.resource_cost

        expires_round = (
            round_number + action.duration_rounds
            if action.duration_rounds is not None else None
        )
        applied: list[str] = []
        for condition_id in action.condition_ids:
            result = apply_timed_condition(
                member.state,
                condition_id,
                member.combatant_id,
                source_effect_id=action.id,
                applied_round=round_number,
                expires_round=expires_round,
                expires_at_start_of_source_turn=False,
                ends_on_owner_attack=action.ends_on_owner_attack,
                ends_on_owner_spell_cast=action.ends_on_owner_spell_cast,
                affected_states=affected_states,
            )
            if result is not None:
                applied.append(result)

        if action.concentration:
            start_concentration(
                member.state,
                member.combatant_id,
                action.id,
                round_number,
                affected_states,
                expires_round=expires_round,
            )

        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            target_id=member.combatant_id,
            target_name=member.state.template.name,
            applied_condition_ids=applied,
            feature_id=action.id,
            resource_remaining=resource.current_uses if resource is not None else None,
            concentration_started_effect_id=action.id if action.concentration else None,
            animation=action.animation,
            description=f"{member.state.template.name} uses {action.name}.",
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Timed self-buff resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff could not be resolved.") from exc
