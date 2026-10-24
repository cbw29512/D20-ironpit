from __future__ import annotations

import logging

from app.domain.capability_effects import SaveConditionEffectDefinition
from app.domain.weapons import OnHitConditionSave
from scripts.browser_on_hit_condition_serializer import serialize_on_hit_condition_save

logger = logging.getLogger(__name__)


def test_indefinite_repeat_save_condition_is_valid_and_serializes_start_turn_damage() -> None:
    try:
        effect = OnHitConditionSave(
            save_ability="constitution",
            dc=21,
            condition_id="poisoned",
            repeat_save_timing="target_turn_end",
            cannot_regain_hit_points=True,
            start_of_turn_damage_dice_count=6,
            start_of_turn_damage_dice_size=6,
            start_of_turn_damage_type="poison",
        )
        row = serialize_on_hit_condition_save(effect)

        assert row == {
            "saveAbility": "constitution",
            "dc": 21,
            "conditionId": "poisoned",
            "maxTargetSize": None,
            "repeatSaveTiming": "target_turn_end",
            "cannotRegainHitPoints": True,
            "startOfTurnDamageDiceCount": 6,
            "startOfTurnDamageDiceSize": 6,
            "startOfTurnDamageType": "poison",
        }
    except Exception:
        logger.exception("Indefinite repeat-save browser serialization regression failed.")
        raise


def test_capability_schema_accepts_repeat_save_until_success_without_duration() -> None:
    try:
        effect = SaveConditionEffectDefinition(
            save_ability="constitution",
            dc=21,
            condition="poisoned",
            repeat_save_timing="target_turn_end",
            cannot_regain_hit_points=True,
            start_of_turn_damage_dice_count=6,
            start_of_turn_damage_dice_size=6,
            start_of_turn_damage_type="poison",
        )

        assert effect.duration_rounds is None
        assert effect.repeat_save_failure_condition is None
        assert effect.repeat_save_timing == "target_turn_end"
    except Exception:
        logger.exception("Indefinite repeat-save capability regression failed.")
        raise
