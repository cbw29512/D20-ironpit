from __future__ import annotations

from app.domain.actions import HitControlEffect
from app.domain.capability_effects import (
    ConditionEffectDefinition,
    ControlEffectDefinition,
    ForcedMovementEffectDefinition,
    GrappleEffectDefinition,
)


def compile_control(effect: ControlEffectDefinition | None) -> HitControlEffect | None:
    if effect is None:
        return None
    if isinstance(effect, ForcedMovementEffectDefinition):
        return HitControlEffect(
            max_target_size=effect.max_target_size,
            forced_movement=effect.movement,
        )
    if isinstance(effect, GrappleEffectDefinition):
        return HitControlEffect(
            max_target_size=effect.max_target_size,
            forced_movement=effect.forced_movement,
            grapple_escape_dc=effect.escape_dc,
            restrains_while_grappled=effect.restrains,
        )
    if isinstance(effect, ConditionEffectDefinition):
        return HitControlEffect(
            max_target_size=effect.max_target_size,
            forced_movement=effect.forced_movement,
            condition_id=effect.condition,
            expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
            expiry_timing=effect.expiry_timing,
            repeat_save_ability=effect.repeat_save_ability,
            repeat_save_dc=effect.repeat_save_dc,
            repeat_save_timing=effect.repeat_save_timing,
            allowed_removal_action_ids=effect.allowed_removal_action_ids,
        )
    raise TypeError(f"Unsupported control capability: {effect!r}")
