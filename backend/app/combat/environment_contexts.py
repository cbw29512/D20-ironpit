from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.environment_contexts import EnvironmentContextId, EnvironmentContextRollKind

logger = logging.getLogger(__name__)


def _removed_from_battlefield(state) -> bool:
    return any(effect.removed_from_battlefield for effect in state.timed_effects)


def _active_emitting_actions(source: EncounterCombatant):
    try:
        active_ids = {
            effect.source_effect_id
            for effect in source.state.timed_effects
            if effect.source_id == source.combatant_id and effect.source_effect_id
        }
        return [
            action
            for action in source.state.template.timed_self_buff_actions
            if action.id in active_ids and action.emitted_environment_contexts
        ]
    except Exception as exc:
        logger.exception("Failed to discover emitted environment contexts for %s.", source.combatant_id)
        raise RuntimeError("Environment context discovery failed.") from exc


def _active_emitted_contexts(source: EncounterCombatant):
    """Combine immutable emissions with currently active effect emissions."""
    yield from source.state.template.emitted_environment_contexts
    for action in source.state.template.environment_context_control_actions:
        mode_id = source.state.environment_context_modes.get(action.id, action.initial_mode_id)
        mode = next((item for item in action.modes if item.id == mode_id), None)
        if mode is None:
            raise ValueError(f"Unknown environment mode {mode_id} for {action.name}.")
        yield from mode.emitted_contexts
    for action in _active_emitting_actions(source):
        yield from action.emitted_environment_contexts


def _context_satisfies(emitted: EnvironmentContextId, requested: EnvironmentContextId) -> bool:
    # Sunlight is always bright light, while ordinary bright light is not sunlight.
    return emitted == requested or (requested == "bright_light" and emitted == "sunlight")


def actor_inside_environment_context(
    actor: EncounterCombatant,
    setup: EncounterSetup | None,
    context_id: EnvironmentContextId,
) -> bool:
    """True when a live source-owned context of this type covers the actor."""
    try:
        if setup is None:
            return False
        for source in [*setup.heroes, *setup.monsters]:
            if _removed_from_battlefield(source.state):
                continue
            for context in _active_emitted_contexts(source):
                if not _context_satisfies(context.context_id, context_id):
                    continue
                if combatant_distance(source, actor) <= context.radius_ft:
                    return True
        return False
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Failed to test environment context %s for %s.", context_id, actor.combatant_id)
        raise RuntimeError("Environment context coverage could not be evaluated.") from exc


def expire_prohibited_timed_self_buffs(setup: EncounterSetup) -> list[str]:
    """End source-owned buffs as soon as their prohibited context covers the owner."""
    try:
        expired: list[str] = []
        for member in [*setup.heroes, *setup.monsters]:
            actions = {
                action.id: action
                for action in member.state.template.timed_self_buff_actions
                if action.prohibited_environment_context_id is not None
            }
            for effect in list(member.state.timed_effects):
                action = actions.get(effect.source_effect_id)
                if action is None or effect.source_id != member.combatant_id:
                    continue
                if not actor_inside_environment_context(
                    member, setup, action.prohibited_environment_context_id,
                ):
                    continue
                from app.combat.timed_condition_lifecycle import remove_effect_group
                remove_effect_group(member.state, effect)
                expired.append(f"{member.state.template.name}'s {action.name}")
        return expired
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Failed prohibited-context timed-buff expiry.")
        raise RuntimeError("Prohibited-context timed buffs could not be expired.") from exc


def environment_context_disadvantage_sources(
    actor: EncounterCombatant,
    setup: EncounterSetup | None,
    roll_kind: EnvironmentContextRollKind,
) -> int:
    """Count target-owned context reactions that impose Disadvantage on this roll."""
    try:
        if setup is None:
            return 0
        count = 0
        for reaction in actor.state.template.environment_context_reactions:
            if roll_kind not in reaction.disadvantage_on:
                continue
            if actor_inside_environment_context(actor, setup, reaction.context_id):
                count += 1
        return count
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Failed to count environment-context Disadvantage for %s.", actor.combatant_id)
        raise RuntimeError("Environment context reaction could not be resolved.") from exc
