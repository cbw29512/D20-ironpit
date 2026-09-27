from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.resources import resource_state
from app.combat.timed_conditions import apply_timed_condition
from app.domain.actions import HpThresholdConditionAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def legal_hp_threshold_condition(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: HpThresholdConditionAction,
) -> bool:
    try:
        if not is_available(actor.state, action.action_cost):
            return False
        if target.state.is_dead or not target.state.is_alive or target.state.current_hp <= 0:
            return False
        if target.state.current_hp > action.max_current_hp:
            return False
        if combatant_distance(actor, target) > action.range_ft:
            return False
        if action.resource_id:
            resource = resource_state(actor.state, action.resource_id)
            if resource is None:
                raise ValueError(f"{action.name} references missing resource {action.resource_id}.")
            if resource.current_uses < action.resource_cost:
                return False
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("HP-threshold condition legality failed for %s.", actor.combatant_id)
        raise RuntimeError("HP-threshold condition legality could not be resolved.") from exc


def choose_hp_threshold_condition(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[EncounterCombatant, HpThresholdConditionAction] | None:
    try:
        for action in actor.state.template.hp_threshold_condition_actions:
            for target in living_opponents(actor, setup):
                if legal_hp_threshold_condition(actor, target, action):
                    return target, action
        return None
    except Exception as exc:
        logger.exception("HP-threshold condition selection failed for %s.", actor.combatant_id)
        raise RuntimeError("HP-threshold condition could not be selected.") from exc


def resolve_hp_threshold_condition(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: HpThresholdConditionAction,
    setup: EncounterSetup,
) -> BattleEvent:
    try:
        if not legal_hp_threshold_condition(actor, target, action):
            raise ValueError(f"{action.name} is not legal against {target.state.template.name}.")
        if action.resource_id:
            resource = resource_state(actor.state, action.resource_id)
            if resource is None:
                raise ValueError(f"{action.name} references missing resource {action.resource_id}.")
            resource.current_uses -= action.resource_cost
            remaining = resource.current_uses
        else:
            remaining = None
        spend(actor.state, action.action_cost)
        applied = apply_timed_condition(
            target.state,
            action.condition_id,
            actor.combatant_id,
            source_effect_id=action.id,
            source_template=actor.state.template,
            source_is_magical=action.magical_effect,
            applied_round=round_number,
            repeat_save_ability=action.repeat_save_ability,
            repeat_save_dc=action.repeat_save_dc,
            repeat_save_timing=action.repeat_save_timing,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
            use_default_poison_recovery=False,
        )
        if applied is None:
            raise ValueError(f"{action.name} could not apply {action.condition_id}.")
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            applied_condition_ids=[applied],
            feature_id=action.id,
            resource_remaining=remaining,
            animation=action.animation,
            description=(
                f"{actor.state.template.name} uses {action.name} on {target.state.template.name}; "
                f"{target.state.template.name} is {action.condition_id.title()}."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("HP-threshold condition resolution failed for %s.", actor.combatant_id)
        raise RuntimeError("HP-threshold condition could not be resolved.") from exc
