from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.instant_death import apply_instant_death
from app.combat.resources import resource_state
from app.domain.actions import HpThresholdInstantDeathAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.combat.zero_hp_replacement import consume_zero_hp_replacement_log

logger = logging.getLogger(__name__)


def legal_hp_threshold_instant_death(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: HpThresholdInstantDeathAction,
) -> bool:
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


def choose_hp_threshold_instant_death(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[EncounterCombatant, HpThresholdInstantDeathAction] | None:
    for action in actor.state.template.hp_threshold_instant_death_actions:
        for target in living_opponents(actor, setup):
            if legal_hp_threshold_instant_death(actor, target, action):
                return target, action
    return None


def resolve_hp_threshold_instant_death(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: HpThresholdInstantDeathAction,
    setup: EncounterSetup,
) -> BattleEvent:
    if not legal_hp_threshold_instant_death(actor, target, action):
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
    hp_before = target.state.current_hp
    outcome = apply_instant_death(
        target.state,
        affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
    )
    prevented = outcome == "instant_death_prevented"
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=actor.combatant_id,
        actor_name=actor.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        hp_before=hp_before,
        hp_after=target.state.current_hp,
        is_dead=target.state.is_dead,
        feature_id=action.id,
        resource_remaining=remaining,
        animation=action.animation,
        description=(
            f"{actor.state.template.name} uses {action.name} on {target.state.template.name}; "
            + (f"{target.state.template.name} dies." if not prevented else f"{target.state.template.name}'s ward negates the instant-death effect.")
            + consume_zero_hp_replacement_log(target.state)
        ),
    )
