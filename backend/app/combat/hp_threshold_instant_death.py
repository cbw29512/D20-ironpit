from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.condition_rules import can_see
from app.combat.hp_threshold_outcome import resolve_threshold_target
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.resources import resource_state


def legal_hp_threshold_instant_death(actor, target, action) -> bool:
    try:
        if not is_available(actor.state, action.action_cost):
            return False
        if target.state.is_dead or not target.state.is_alive or target.state.current_hp <= 0:
            return False
        if target.state.current_hp > action.max_current_hp and not action.fallback_damage_dice_count:
            return False
        # Source data owns visibility; all sources share the ordinary sight predicate.
        distance = combatant_distance(actor, target)
        if action.requires_target_sight and not can_see(actor.state, target.state, distance):
            return False
        if distance > action.range_ft:
            return False
        if action.resource_id:
            resource = resource_state(actor.state, action.resource_id)
            if resource is None:
                raise ValueError(f"{action.name} references missing resource {action.resource_id}.")
            if resource.current_uses < action.resource_cost:
                return False
        return True
    except Exception:
        logging.getLogger(__name__).exception("HP-threshold death legality failed for %s.", actor.combatant_id)
        raise


def choose_hp_threshold_instant_death(actor, setup):
    try:
        for action in actor.state.template.hp_threshold_instant_death_actions:
            for target in living_opponents(actor, setup):
                if legal_hp_threshold_instant_death(actor, target, action):
                    return target, action
        return None
    except Exception:
        logging.getLogger(__name__).exception("Threshold choose_hp_threshold_instant_death failed for %s.", actor.combatant_id)
        raise


def choose_hp_threshold_instant_death_targets(actor, setup):
    try:
        selected = choose_hp_threshold_instant_death(actor, setup)
        if selected is None:
            return None
        primary, action = selected
        targets = [primary]
        if action.max_targets > 1:
            for target in living_opponents(actor, setup):
                if target.combatant_id == primary.combatant_id:
                    continue
                if not legal_hp_threshold_instant_death(actor, target, action):
                    continue
                if (
                    action.secondary_target_within_ft is not None
                    and combatant_distance(primary, target) > action.secondary_target_within_ft
                ):
                    continue
                targets.append(target)
                if len(targets) >= action.max_targets:
                    break
        return targets, action
    except Exception:
        logging.getLogger(__name__).exception("Threshold choose_hp_threshold_instant_death_targets failed for %s.", actor.combatant_id)
        raise


def _spend_once(actor, action):
    try:
        remaining = None
        if action.resource_id:
            resource = resource_state(actor.state, action.resource_id)
            if resource is None:
                raise ValueError(f"{action.name} references missing resource {action.resource_id}.")
            resource.current_uses -= action.resource_cost
            remaining = resource.current_uses
        spend(actor.state, action.action_cost)
        return remaining


    except Exception:
        logging.getLogger(__name__).exception("Threshold _spend_once failed for %s.", actor.combatant_id)
        raise


def resolve_hp_threshold_instant_death(
    sequence, round_number, actor, target, action, setup, *, dice=None,
):
    try:
        if not legal_hp_threshold_instant_death(actor, target, action):
            raise ValueError(f"{action.name} is not legal against {target.state.template.name}.")
        remaining = _spend_once(actor, action)
        return resolve_threshold_target(sequence, round_number, actor, target, action, setup, remaining, dice)
    except Exception:
        logging.getLogger(__name__).exception("Threshold resolve_hp_threshold_instant_death failed for %s.", actor.combatant_id)
        raise


def resolve_group_hp_threshold_instant_death(
    sequence, round_number, actor, targets, action, setup, *, dice=None,
):
    try:
        if not targets or len(targets) > action.max_targets:
            raise ValueError("Threshold action target count is illegal.")
        if any(not legal_hp_threshold_instant_death(actor, target, action) for target in targets):
            raise ValueError("Threshold action contains an illegal target.")
        if action.secondary_target_within_ft is not None and len(targets) > 1:
            primary = targets[0]
            if any(
                combatant_distance(primary, target) > action.secondary_target_within_ft
                for target in targets[1:]
            ):
                raise ValueError("Threshold secondary target violates linked-target distance.")
        remaining = _spend_once(actor, action)
        return [
            resolve_threshold_target(sequence + index, round_number, actor, target, action, setup, remaining, dice)
            for index, target in enumerate(targets)
        ]
    except Exception:
        logging.getLogger(__name__).exception("Threshold resolve_group_hp_threshold_instant_death failed for %s.", actor.combatant_id)
        raise
