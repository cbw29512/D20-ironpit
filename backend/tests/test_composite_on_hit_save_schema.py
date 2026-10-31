"""One-saving-throw composite effect schema: no second save or source dispatch."""
from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from app.domain.weapons import OnHitSaveDamage
from app.domain.on_hit_conditions import OnHitConditionSave

logger = logging.getLogger(__name__)


def _damage(**changes):
    try:
        values = dict(
            source="Synthetic Poison", save_ability="constitution", dc=10,
            dice_count=2, dice_size=4, damage_type="poison",
            success_damage="none",
            failed_save_condition=OnHitConditionSave(
                save_ability="constitution", dc=10,
                condition_id="poisoned", duration_rounds=10,
                repeat_save_timing="target_turn_end",
            ),
        )
        values.update(changes)
        return OnHitSaveDamage(**values)
    except Exception:
        logger.exception("Composite save schema construction failed")
        raise


def test_composite_save_keeps_source_owned_parameters():
    try:
        rule = _damage()
        assert rule.failed_save_condition is not None
        assert rule.failed_save_condition.dc == rule.dc
        assert rule.failed_save_condition.condition_id == "poisoned"
        assert rule.success_damage == "none"
    except Exception:
        logger.exception("Composite schema data test failed")
        raise


@pytest.mark.parametrize("override", [
    {"failed_save_condition": OnHitConditionSave(
        save_ability="wisdom", dc=10, condition_id="poisoned",
    )},
    {"failed_save_condition": OnHitConditionSave(
        save_ability="constitution", dc=11, condition_id="poisoned",
    )},
])
def test_inconsistent_saving_throw_rejected(override):
    try:
        with pytest.raises(ValidationError):
            _damage(**override)
    except Exception:
        logger.exception("Composite save mismatch rejection test failed")
        raise
