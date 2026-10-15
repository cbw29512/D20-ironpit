from __future__ import annotations
import pytest
from app.combat.turn_start_visual_policy import (
    VisualTurnStartFacts, VisualTurnStartRule,
    decide_visual_turn_start, resolve_visual_save_stage,
)

BASILISK = VisualTurnStartRule("source-1", "Petrifying Gaze", 30, 12)
MEDUSA = VisualTurnStartRule("source-2", "Petrifying Gaze", 30, 14, immediate_petrification_margin=5)

def _facts(**overrides):
    defaults = dict(distance_ft=15, source_active=True, target_active=True,
                    source_sees_target=True, target_sees_source=True,
                    target_immune=False, target_surprised=False, may_avert_eyes=True)
    defaults.update(overrides)
    return VisualTurnStartFacts(**defaults)

@pytest.mark.parametrize("rule", [BASILISK, MEDUSA])
def test_automatic_aversion_and_surprise(rule):
    assert decide_visual_turn_start(rule, _facts()) == "averted"
    assert decide_visual_turn_start(rule, _facts(may_avert_eyes=False)) == "save_required"
    assert decide_visual_turn_start(rule, _facts(target_surprised=True)) == "save_required"

@pytest.mark.parametrize("override", [
    {"distance_ft": 31}, {"source_active": False}, {"target_active": False},
    {"source_sees_target": False}, {"target_sees_source": False}, {"target_immune": True},
])
def test_visibility_range_immunity_and_liveness(override):
    assert decide_visual_turn_start(MEDUSA, _facts(**override)) == "ineligible"

def test_staged_save_transitions_and_source_parameters():
    assert resolve_visual_save_stage(BASILISK, 1) == "restrained"
    assert resolve_visual_save_stage(BASILISK, 12) == "clear"
    assert resolve_visual_save_stage(BASILISK, 1, previous_stage="restrained") == "petrified"
    assert resolve_visual_save_stage(BASILISK, 12, previous_stage="restrained") == "clear"
    assert resolve_visual_save_stage(MEDUSA, 10) == "restrained"
    assert resolve_visual_save_stage(MEDUSA, 9) == "petrified"
    renamed = VisualTurnStartRule("other", "Unrelated Label", 30, 14, immediate_petrification_margin=5)
    assert resolve_visual_save_stage(renamed, 9) == "petrified"

def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        VisualTurnStartRule("", "label", 30, 12)
    with pytest.raises(ValueError):
        VisualTurnStartRule("id", "label", 0, 12)
    with pytest.raises(ValueError):
        decide_visual_turn_start(BASILISK, _facts(distance_ft=-1))
    with pytest.raises(ValueError):
        resolve_visual_save_stage(MEDUSA, 4, previous_stage="unknown")
