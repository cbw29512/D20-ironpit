from __future__ import annotations

import logging

from app.domain.actions import HitControlEffect
from app.domain.capability_effects import ConditionEffectDefinition, GrappleEffectDefinition

logger = logging.getLogger(__name__)


class UnsupportedAttackControlError(ValueError):
    pass


def compile_control(effect: GrappleEffectDefinition | ConditionEffectDefinition) -> HitControlEffect:
    try:
        if isinstance(effect, GrappleEffectDefinition):
            return HitControlEffect(
                max_target_size=effect.max_target_size,
                grapple_escape_dc=effect.escape_dc,
                restrains_while_grappled=effect.restrains,
                conditions_while_grappled=effect.linked_conditions,
            )
        return HitControlEffect(
            max_target_size=effect.max_target_size,
            condition_id=effect.condition,
            expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
            expiry_timing=effect.expiry_timing,
            repeat_save_ability=effect.repeat_save_ability,
            repeat_save_dc=effect.repeat_save_dc,
            repeat_save_timing=effect.repeat_save_timing,
            repeat_save_delay_rounds=effect.repeat_save_delay_rounds,
            allowed_removal_action_ids=effect.allowed_removal_action_ids,
        )
    except Exception:
        logger.exception("Failed to compile attack control effect %r.", effect)
        raise


def merge_controls(controls: list[HitControlEffect]) -> HitControlEffect | None:
    try:
        if not controls:
            return None
        if len(controls) == 1:
            return controls[0]
        grapple = next((item for item in controls if item.grapple_escape_dc is not None), None)
        condition = next((item for item in controls if item.condition_id is not None), None)
        if grapple is None or condition is None or len(controls) != 2:
            raise UnsupportedAttackControlError("Attack control riders cannot be composed by the shared control model.")
        size_limits = [item.max_target_size for item in controls if item.max_target_size is not None]
        if len(set(size_limits)) > 1:
            raise UnsupportedAttackControlError("Composable attack control riders must share the same target-size limit.")
        return HitControlEffect(
            max_target_size=size_limits[0] if size_limits else None,
            grapple_escape_dc=grapple.grapple_escape_dc,
            restrains_while_grappled=grapple.restrains_while_grappled,
            conditions_while_grappled=grapple.conditions_while_grappled,
            condition_id=condition.condition_id,
            expires_at_start_of_source_turn=condition.expires_at_start_of_source_turn,
            expiry_timing=condition.expiry_timing,
            repeat_save_ability=condition.repeat_save_ability,
            repeat_save_dc=condition.repeat_save_dc,
            repeat_save_timing=condition.repeat_save_timing,
            repeat_save_delay_rounds=condition.repeat_save_delay_rounds,
            allowed_removal_action_ids=condition.allowed_removal_action_ids,
        )
    except UnsupportedAttackControlError:
        raise
    except Exception:
        logger.exception("Failed to merge attack control riders.")
        raise
