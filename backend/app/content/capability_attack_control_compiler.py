from __future__ import annotations

import logging

from app.domain.actions import HitControlEffect
from app.domain.capability_effects import ConditionEffectDefinition, GrappleEffectDefinition

logger = logging.getLogger(__name__)


def compile_attack_control(
    effect: GrappleEffectDefinition | ConditionEffectDefinition,
) -> HitControlEffect:
    try:
        if isinstance(effect, GrappleEffectDefinition):
            return HitControlEffect(
                max_target_size=effect.max_target_size,
                grapple_escape_dc=effect.escape_dc,
                restrains_while_grappled=effect.restrains,
                grapple_requires_source_free=effect.requires_source_free,
                grapple_periodic_damage=effect.periodic_damage,
            )
        return HitControlEffect(
            max_target_size=effect.max_target_size,
            condition_id=effect.condition,
            expires_at_start_of_source_turn=effect.expires_at_start_of_source_turn,
            expiry_timing=effect.expiry_timing,
            repeat_save_ability=effect.repeat_save_ability,
            repeat_save_dc=effect.repeat_save_dc,
            repeat_save_timing=effect.repeat_save_timing,
            allowed_removal_action_ids=effect.allowed_removal_action_ids,
        )
    except Exception:
        logger.exception("Failed to compile attack control effect.")
        raise
