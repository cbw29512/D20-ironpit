"""Fail-closed card validation for source-neutral failed-save escalation."""
from __future__ import annotations

import pytest

from app.content.monster_attack_effect_validation_2014 import supported_save_condition_2014
from app.domain.capability_effects import SaveConditionEffectDefinition
from app.domain.weapons import OnHitConditionSave


ESCALATION = {"margin": 5, "additional_condition_ids": ["unconscious"]}


@pytest.mark.parametrize("schema,field", [
    (SaveConditionEffectDefinition, "condition"),
    (OnHitConditionSave, "condition_id"),
])
def test_escalation_without_any_expiry_is_rejected_at_schema_boundary(schema, field):
    with pytest.raises(ValueError, match="requires duration_rounds"):
        schema.model_validate({
            "save_ability": "constitution", "dc": 12,
            field: "poisoned", "failure_margin_escalation": ESCALATION,
        })


@pytest.mark.parametrize("schema,field", [
    (SaveConditionEffectDefinition, "condition"),
    (OnHitConditionSave, "condition_id"),
])
def test_escalation_with_base_or_replacement_duration_is_legal(schema, field):
    base = {"save_ability": "constitution", "dc": 12, field: "poisoned"}
    assert schema.model_validate({
        **base, "duration_rounds": 10, "failure_margin_escalation": ESCALATION,
    }).failure_margin_escalation is not None
    assert schema.model_validate({
        **base, "failure_margin_escalation": {
            **ESCALATION, "replacement_duration_dice_count": 1,
            "replacement_duration_dice_size": 10,
            "replacement_duration_round_multiplier": 10,
        },
    }).failure_margin_escalation is not None


def test_source_2014_classifier_rejects_expiryless_escalation():
    row = {
        "save_ability": "constitution", "dc": 12,
        "condition_id": "poisoned", "failure_margin_escalation": ESCALATION,
    }
    assert supported_save_condition_2014(row) is False
    assert supported_save_condition_2014({**row, "duration_rounds": 10}) is True
