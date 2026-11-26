from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance
from app.combat.owner_action_expiry import expire_on_owner_event
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.environment_contexts import EnvironmentContextControlAction, EnvironmentContextMode
from app.domain.events import BattleEvent

logger = logging.getLogger(__name__)


def choose_environment_context_action(
    member: EncounterCombatant, setup: EncounterSetup,
) -> tuple[EnvironmentContextControlAction, EnvironmentContextMode] | None:
    """Choose a source-declared mode only when it creates a live hostile rider."""
    try:
        enemies = setup.monsters if member.side == "heroes" else setup.heroes
        for action in member.state.template.environment_context_control_actions:
            if not is_available(member.state, action.action_cost):
                continue
            current = member.state.environment_context_modes.get(action.id, action.initial_mode_id)
            if current == action.ai_mode_id:
                continue
            mode = next(item for item in action.modes if item.id == action.ai_mode_id)
            relevant = any(
                reaction.context_id == emitted.context_id
                and combatant_distance(member, enemy) <= emitted.radius_ft
                for emitted in mode.emitted_contexts
                for enemy in enemies if enemy.state.is_alive and not enemy.state.is_dead
                for reaction in enemy.state.template.environment_context_reactions
            )
            if relevant:
                return action, mode
        return None
    except Exception as exc:
        logger.exception("Environment context action policy failed for %s.", member.combatant_id)
        raise RuntimeError("Environment context action could not be selected.") from exc


def resolve_environment_context_action(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    action: EnvironmentContextControlAction,
    mode: EnvironmentContextMode,
    *,
    affected_states=None,
    setup: EncounterSetup | None = None,
) -> BattleEvent:
    """Spend printed economy and update only fight-local mode state."""
    try:
        if mode.id not in {item.id for item in action.modes}:
            raise ValueError(f"{mode.id} is not a declared mode for {action.name}.")
        if not is_available(member.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        current = member.state.environment_context_modes.get(action.id, action.initial_mode_id)
        if current == mode.id:
            raise ValueError(f"{action.name} is already in mode {mode.id}.")
        spend(member.state, action.action_cost)
        expire_on_owner_event(
            member.state, "action", affected_states or [member.state], action_id=action.id,
        )
        member.state.environment_context_modes[action.id] = mode.id
        expired: list[str] = []
        if setup is not None:
            from app.combat.environment_contexts import expire_prohibited_timed_self_buffs
            expired = expire_prohibited_timed_self_buffs(setup)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=member.state.template.name,
            feature_id=action.name,
            animation="buff",
            description=(
                f"{member.state.template.name} uses {action.name} and selects {mode.id}."
                + (f" {', '.join(expired)} ends." if expired else "")
            ),
        )
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Environment context action failed for %s.", member.combatant_id)
        raise RuntimeError("Environment context action could not be resolved.") from exc
