"""Universal Swallow state transitions for source-proven grapple-Bite actions.

The caller must spend an action and resolve the source's printed bite hit first.
This module owns only validated condition/ownership transitions, not AI policy.
"""
from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.grapple import release_grapple
from app.domain.models import CombatantState
from app.domain.size import size_at_most
from app.domain.swallowed_state import SwallowedState
from app.domain.swallow_actions import GrappleSwallowAction

_SWALLOW_CONDITIONS = ("blinded", "restrained")


def swallow_after_bite(
    owner_id: str, owner: CombatantState,
    target_id: str, target: CombatantState,
    action: GrappleSwallowAction, *, bite_hit: bool,
) -> bool:
    """End owned grapple and place a size-legal target in fight-only Swallow."""
    if not bite_hit:
        return False
    if not owner.is_alive or owner.is_dead or owner.current_hp <= 0:
        return False
    if target.is_dead or not target.is_alive or target.current_hp <= 0:
        return False
    if target.swallowed is not None:
        return False
    if not size_at_most(target.template.size, action.max_target_size):
        return False
    if len(owner.swallowed_target_ids) >= action.max_swallowed:
        return False
    if (action.requires_existing_grapple and not any(
        held.source_id == owner_id for held in target.grapple_sources
    )):
        return False
    if action.attack_id not in {
        attack.id for attack in (
            [owner.template.weapon_attack] if owner.template.weapon_attack else []
        ) + owner.template.alternate_weapon_attacks
    }:
        raise ValueError("Swallow must reference a source-proven owned attack.")
    release_grapple(target, owner_id)
    target.swallowed = SwallowedState(
        source_id=owner_id, source_name=action.source_name,
        damage_dice_count=action.damage_dice_count,
        damage_dice_size=action.damage_dice_size,
        damage_type=action.damage_type,
        exit_movement_ft=action.exit_movement_ft,
        target_size=action.max_target_size,
    )
    owner.swallowed_target_ids.append(target_id)
    for condition in _SWALLOW_CONDITIONS:
        if not condition_is_immune(target, condition) and condition not in target.active_effect_ids:
            target.active_effect_ids.append(condition)
    target.active_effect_ids = [
        item for item in target.active_effect_ids if item != "dodge"
    ]
    return True


def release_swallowed(
    owner: CombatantState, target_id: str, target: CombatantState,
    *, owner_id: str, exiting_prone: bool = True,
) -> bool:
    """Release target on source death; never clear unrelated condition owners."""
    if target.swallowed is None or target.swallowed.source_id != owner_id:
        return False
    if target_id in owner.swallowed_target_ids:
        owner.swallowed_target_ids.remove(target_id)
    target.swallowed = None
    # Source-bound swallowed conditions are removed only when no independent
    # timed effect or grapple still owns the same condition.
    for condition in _SWALLOW_CONDITIONS:
        independently_owned = (
            any(item.restrains for item in target.grapple_sources) if condition == "restrained"
            else False
        ) or any(item.effect_id == condition for item in target.timed_effects)
        if not independently_owned:
            target.active_effect_ids = [x for x in target.active_effect_ids if x != condition]
    if exiting_prone and not condition_is_immune(target, "prone"):
        if "prone" not in target.active_effect_ids:
            target.active_effect_ids.append("prone")
    return True
