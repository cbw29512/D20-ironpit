from __future__ import annotations

import logging

from app.domain.capability_effects import SaveConditionEffectDefinition, SavePersistentEffectDefinition
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


def test_source_only_delayed_fields_fail_closed_at_runtime_boundary() -> None:
    try:
        OnHitConditionSave.model_validate({
            "save_ability": "constitution",
            "dc": 12,
            "effect_id": "synthetic-rot",
            "delayed_max_hp_reduction_delay_hours": 24,
        })
    except ValueError as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("Source-only delayed metadata entered the combat schema.")


def test_persistent_failed_save_effect_serializes_only_arena_active_state() -> None:
    try:
        definition = SavePersistentEffectDefinition(
            save_ability="constitution", dc=12, effect_id="synthetic-rot",
            curse_id="synthetic-rot", cannot_regain_hit_points=True,
            allowed_removal_action_ids=["remove-curse"],
        )
        effect = OnHitConditionSave(
            save_ability=definition.save_ability, dc=definition.dc,
            effect_id=definition.effect_id, curse_id=definition.curse_id,
            cannot_regain_hit_points=definition.cannot_regain_hit_points,
            allowed_removal_action_ids=definition.allowed_removal_action_ids,
        )
        row = serialize_on_hit_condition_save(effect)
        assert row["conditionId"] is None
        assert row["effectId"] == "synthetic-rot"
        assert row["curseId"] == "synthetic-rot"
        assert row["cannotRegainHitPoints"] is True
        assert row["allowedRemovalActionIds"] == ["remove-curse"]
        assert "delayedMaxHpReduction" not in row
    except Exception:
        logger.exception("Persistent failed-save browser serialization regression failed.")
        raise
