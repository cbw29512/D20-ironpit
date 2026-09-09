from __future__ import annotations

from typing import Any


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


def _movement(effect: Any) -> dict[str, Any] | None:
    movement = getattr(effect, "forced_movement", None)
    if movement is None:
        return None
    return {
        "direction": movement.direction,
        "maxDistanceFt": movement.max_distance_ft,
        "distanceMode": movement.distance_mode,
    }


def control_row(effect: Any) -> dict[str, Any] | None:
    if effect is None:
        return None
    row: dict[str, Any] = {}
    if effect.max_target_size is not None:
        row["maxTargetSize"] = _value(effect.max_target_size)
    movement = _movement(effect)
    if movement is not None:
        row["forcedMovement"] = movement
    if effect.grapple_escape_dc is not None:
        row["grappleEscapeDc"] = effect.grapple_escape_dc
    if effect.restrains_while_grappled:
        row["restrainsWhileGrappled"] = True
    if effect.condition_id is not None:
        row["conditionId"] = effect.condition_id
    if effect.expires_at_start_of_source_turn:
        row["expiresAtStartOfSourceTurn"] = True
    if effect.expiry_timing is not None:
        row["expiryTiming"] = effect.expiry_timing
    if effect.repeat_save_ability is not None:
        row["repeatSaveAbility"] = effect.repeat_save_ability
        row["repeatSaveDc"] = effect.repeat_save_dc
        row["repeatSaveTiming"] = effect.repeat_save_timing
    if effect.allowed_removal_action_ids:
        row["allowedRemovalActionIds"] = list(effect.allowed_removal_action_ids)
    return row or None


def enrich_control_rows(row: dict[str, Any], template: Any) -> dict[str, Any]:
    """Overlay universal control data until the legacy serializer is fully split."""
    attacks = {item.id: item for item in [template.weapon_attack, *template.alternate_weapon_attacks]}
    for attack_row in row.get("attacks", []):
        attack = attacks.get(attack_row.get("id"))
        if attack is None:
            continue
        control = control_row(attack.control_effect)
        if control is not None:
            attack_row["controlEffect"] = control
    saves = {item.id: item for item in template.saving_throw_actions}
    for save_row in row.get("saving_throw_actions", []):
        action = saves.get(save_row.get("id"))
        if action is None:
            continue
        control = control_row(action.failure_control)
        if control is not None:
            save_row["failureControl"] = control
    return row
