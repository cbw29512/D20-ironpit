from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.condition_rules import has_condition
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def timed_self_buff_resource(
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
):
    try:
        if action.resource_id is None:
            return None
        return next(
            (item for item in member.state.resources if item.id == action.resource_id),
            None,
        )
    except Exception as exc:
        logger.exception(
            "Timed self-buff resource lookup failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Timed self-buff resource could not be resolved.") from exc


def timed_self_buff_active(
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
) -> bool:
    try:
        return any(
            effect.source_id == member.combatant_id
            and effect.source_effect_id == action.id
            for effect in member.state.timed_effects
        )
    except Exception as exc:
        logger.exception(
            "Timed self-buff activity lookup failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Timed self-buff activity could not be evaluated.") from exc


def _friendly_aura_is_relevant(
    member: EncounterCombatant,
    action: TimedSelfBuffAction,
    setup: EncounterSetup | None,
) -> bool:
    try:
        aura = action.friendly_save_advantage_aura
        if aura is None:
            return True
        if setup is None:
            return False
        allies = setup.heroes if member.side == "heroes" else setup.monsters
        for target in allies:
            if target.state.is_dead or not target.state.is_alive:
                continue
            if combatant_distance(member, target) > aura.radius_ft:
                continue
            if aura.requires_hearing and has_condition(target.state, "deafened"):
                continue
            if any(has_condition(target.state, tag) for tag in aura.required_effect_tags):
                return True
        return False
    except Exception as exc:
        logger.exception(
            "Timed friendly save-aura relevance check failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Timed self-buff relevance could not be evaluated.") from exc


def choose_timed_self_buff_action(
    member: EncounterCombatant,
    setup: EncounterSetup | None = None,
) -> TimedSelfBuffAction | None:
    """Choose the highest-priority legal inactive tactically relevant self-buff."""
    try:
        choices: list[TimedSelfBuffAction] = []
        for action in member.state.template.timed_self_buff_actions:
            resource = timed_self_buff_resource(member, action)
            if (
                is_available(member.state, action.action_cost)
                and (
                    action.resource_id is None
                    or (
                        resource is not None
                        and resource.current_uses >= action.resource_cost
                    )
                )
                and not timed_self_buff_active(member, action)
                and _friendly_aura_is_relevant(member, action, setup)
            ):
                choices.append(action)
        return max(choices, key=lambda item: item.priority, default=None)
    except Exception as exc:
        logger.exception("Timed self-buff choice failed for %s.", member.combatant_id)
        raise RuntimeError("Timed self-buff policy could not be evaluated.") from exc
