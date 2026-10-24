from __future__ import annotations

import logging

from app.content.monster_attack_effect_validation_2014 import (
    ADVANTAGE_TRIGGERS_2014,
    supported_ability_score_reduction_2014,
    supported_contested_movement_2014,
    supported_control_2014,
    supported_damage_row_2014,
    supported_save_condition_2014,
    supported_save_damage_2014,
    supported_save_max_hp_reduction_2014,
)
from app.content.monster_charge_profile_2014 import supports_charge_profile_2014
from app.content.monster_conditional_damage_2014 import supports_conditional_damage_2014
from app.content.monster_grapple_periodic_2014 import supports_grapple_periodic_2014
from app.content.monster_hp_loss_effect_2014 import supported_ongoing_hp_loss_2014
from app.content.monster_source_2014 import SourceAttack2014
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)


def source_conditional_attack_advantage_2014(
    attack: SourceAttack2014,
) -> list[ConditionalAttackAdvantage]:
    try:
        specs: list[ConditionalAttackAdvantage] = []
        for value in attack.conditional_attack_advantage:
            if not isinstance(value, dict) or set(value) != {"trigger"}:
                raise ValueError(
                    f"{attack.id} has unsupported conditional attack Advantage data"
                )
            trigger = str(value["trigger"]).lower()
            if trigger not in ADVANTAGE_TRIGGERS_2014:
                raise ValueError(
                    f"{attack.id} has unsupported conditional attack Advantage trigger {trigger!r}"
                )
            specs.append(ConditionalAttackAdvantage(trigger=trigger))
        return specs
    except Exception:
        logger.exception(
            "Failed to compile conditional attack Advantage for %s.", attack.id
        )
        raise


def supports_basic_attack_effects_2014(attack: SourceAttack2014) -> bool:
    try:
        try:
            source_conditional_attack_advantage_2014(attack)
        except ValueError:
            return False
        if attack.conditional_damage and not all(
            supports_conditional_damage_2014(row) for row in attack.conditional_damage
        ):
            return False
        if (
            attack.on_hit_ability_score_reduction is not None
            and not supported_ability_score_reduction_2014(
                attack.on_hit_ability_score_reduction
            )
        ):
            return False
        if attack.on_hit_save_effect is not None and not (
            supported_save_condition_2014(attack.on_hit_save_effect)
            or supported_save_damage_2014(attack.on_hit_save_effect)
            or supported_save_max_hp_reduction_2014(attack.on_hit_save_effect)
            or supported_ongoing_hp_loss_2014(attack)
        ):
            return False
        if (
            attack.on_hit_contested_movement is not None
            and not supported_contested_movement_2014(
                attack.on_hit_contested_movement
            )
        ):
            return False
        if (
            attack.ongoing_damage_effect
            and not (
                supported_ongoing_hp_loss_2014(attack)
                or supports_grapple_periodic_2014(attack)
            )
        ) or attack.resource_id or attack.breakable_restraint:
            return False
        if (
            attack.charge_profile is not None
            and not supports_charge_profile_2014(attack.charge_profile)
        ):
            return False
        if attack.grapple_target_policy not in {
            "normal", "own_grapple_only", "auto_hit_own_grapple"
        }:
            return False
        if attack.on_hit_damage and not all(
            supported_damage_row_2014(row) for row in attack.on_hit_damage
        ):
            return False
        if (
            attack.control_effect is not None
            and not supported_control_2014(attack.control_effect)
        ):
            return False
        return not (
            attack.forbid_target_grappled_by_self and attack.control_effect is None
        )
    except Exception:
        logger.exception("Failed to classify basic attack effects for %s.", attack.id)
        raise
