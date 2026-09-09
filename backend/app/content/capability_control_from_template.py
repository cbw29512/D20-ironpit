from __future__ import annotations

from app.content.capability_compiler import UnsupportedCapabilityError


def _movement(control) -> dict[str, object] | None:
    effect = control.forced_movement
    if effect is None:
        return None
    return effect.model_dump(mode="json")


def control_definition(control) -> dict[str, object]:
    has_grapple = control.grapple_escape_dc is not None
    has_condition = control.condition_id is not None
    movement = _movement(control)
    if has_grapple and has_condition:
        raise UnsupportedCapabilityError("Runtime control rider combines grapple and condition.")
    if has_grapple:
        return {
            "kind": "grapple",
            "escape_dc": control.grapple_escape_dc,
            "max_target_size": control.max_target_size,
            "restrains": control.restrains_while_grappled,
            "forced_movement": movement,
        }
    if has_condition:
        return {
            "kind": "condition",
            "condition": control.condition_id,
            "max_target_size": control.max_target_size,
            "forced_movement": movement,
            "expires_at_start_of_source_turn": control.expires_at_start_of_source_turn,
            "expiry_timing": control.expiry_timing,
            "repeat_save_ability": control.repeat_save_ability,
            "repeat_save_dc": control.repeat_save_dc,
            "repeat_save_timing": control.repeat_save_timing,
            "allowed_removal_action_ids": control.allowed_removal_action_ids,
        }
    if movement is not None:
        return {
            "kind": "forced_movement",
            "movement": movement,
            "max_target_size": control.max_target_size,
        }
    raise UnsupportedCapabilityError("Runtime control rider has no supported effect.")
