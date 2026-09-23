from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant
from app.domain.events import BattleEvent
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def _resource(member: EncounterCombatant, action: TimedSelfBuffAction):
    return next((item for item in member.state.resources if item.id == action.resource_id), None)


def timed_self_buff_active(member: EncounterCombatant, action: TimedSelfBuffAction) -> bool:
    try:
        return any(
            effect.source_id == member.combatant_id and effect.source_effect_id == action.id
            for effect in member.state.timed_effects
        )
    except Exception as exc:
        logger.exception("Timed self-buff activity lookup failed for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff activity could not be evaluated.") from exc


def choose_timed_self_buff_action(member: EncounterCombatant) -> TimedSelfBuffAction | None:
    """Choose the highest-priority legal inactive self-buff without mutating combat state."""
    try:
        choices = []
        for action in member.state.template.timed_self_buff_actions:
            resource = _resource(member, action)
            if (
                is_available(member.state, action.action_cost)
                and resource is not None
                and resource.current_uses >= action.resource_cost
                and not timed_self_buff_active(member, action)
            ):
                choices.append(action)
        return max(choices, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception("Timed self-buff choice failed for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff policy could not be evaluated.") from exc


def resolve_timed_self_buff(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
) -> BattleEvent:
    """Spend source-defined economy/resources and apply one source-owned timed buff."""
    try:
        resource = _resource(member, action)
        if not is_available(member.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if resource is None or resource.current_uses < action.resource_cost:
            raise ValueError(f"Resource {action.resource_id} is unavailable for {action.name}.")
        if timed_self_buff_active(member, action):
            raise ValueError(f"{action.name} is already active.")

        spend(member.state, action.action_cost)
        resource.current_uses -= action.resource_cost
        applied: list[str] = []
        for index, condition_id in enumerate(action.condition_ids):
            condition = apply_timed_condition(
                member.state,
                condition_id,
                member.combatant_id,
                source_effect_id=action.id,
                source_template=member.state.template,
                applied_round=round_number,
                expires_round=round_number + action.duration_rounds,
                expiry_timing=action.expiry_timing,
                expires_at_start_of_source_turn=action.expiry_timing == "source_turn_start",
                owned_damage_resistances=action.damage_resistances if index == 0 else [],
                use_default_poison_recovery=False,
            )
            if condition is not None:
                applied.append(condition)
        if not applied:
            raise RuntimeError(f"{action.name} applied no timed condition.")

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
            resource_remaining=resource.current_uses,
            animation=action.animation,
            description=f"{member.state.template.name} uses {action.name}.",
        )
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Timed self-buff resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff could not be resolved.") from exc
