from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.domain.turn_start_save_reaction import TurnStartSaveReaction


def _unnerving_mask() -> TurnStartSaveReaction:
    return TurnStartSaveReaction(
        source_id="unnerving-mask",
        source_name="Unnerving Mask",
        range_ft=30,
        source_must_see_target=True,
        target_must_see_source=True,
        save_ability="wisdom",
        save_dc=14,
    )


def test_source_parameters_capture_both_vision_gates_and_turn_expiry() -> None:
    rule = _unnerving_mask()
    assert rule.trigger == "other_creature_turn_start"
    assert rule.range_ft == 30
    assert rule.source_must_see_target and rule.target_must_see_source
    assert rule.save_ability == "wisdom" and rule.save_dc == 14
    assert rule.failure_condition == "frightened"
    assert rule.expires_at == "target_turn_end"


def test_invalid_save_dc_and_range_fail_closed() -> None:
    with pytest.raises(ValidationError):
        TurnStartSaveReaction.model_validate({**_unnerving_mask().model_dump(), "save_dc": 0})
    with pytest.raises(ValidationError):
        TurnStartSaveReaction.model_validate({**_unnerving_mask().model_dump(), "range_ft": 0})
