from __future__ import annotations
import pytest
from app.combat.turn_start_visual_policy import (
    VisualTurnStartFacts, VisualTurnStartRule,
    decide_visual_turn_start, resolve_visual_save_stage,
)

BASILISK = VisualTurnStartRule(source_id="source-1", source_name="Petrifying Gaze", range_ft=30, save_dc=12)
MEDUSA = VisualTurnStartRule(source_id="source-2", source_name="Petrifying Gaze", range_ft=30, save_dc=14, immediate_petrification_margin=5)

def _facts(**overrides):
    defaults = dict(distance_ft=15, source_active=True, target_active=True,
                    source_sees_target=True, target_sees_source=True,
                    target_immune=False, target_surprised=False)
    defaults.update(overrides)
    return VisualTurnStartFacts(**defaults)

@pytest.mark.parametrize("rule", [BASILISK, MEDUSA])
def test_automatic_aversion_and_surprise(rule):
    assert decide_visual_turn_start(rule, _facts()) == "averted"
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
    renamed = VisualTurnStartRule(source_id="other", source_name="Unrelated Label", range_ft=30, save_dc=14, immediate_petrification_margin=5)
    assert resolve_visual_save_stage(renamed, 9) == "petrified"

def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError):
        VisualTurnStartRule(source_id="", source_name="label", range_ft=30, save_dc=12)
    with pytest.raises(ValueError):
        VisualTurnStartRule(source_id="id", source_name="label", range_ft=0, save_dc=12)
    with pytest.raises(ValueError):
        decide_visual_turn_start(BASILISK, _facts(distance_ft=-1))
    with pytest.raises(ValueError):
        resolve_visual_save_stage(MEDUSA, 4, previous_stage="unknown")

@pytest.mark.parametrize("bad", [True, 30.5, "30"])
def test_strict_numeric_visual_source_range(bad):
    with pytest.raises(ValueError):
        VisualTurnStartRule(source_id="source", source_name="Label", range_ft=bad, save_dc=12)

@pytest.mark.parametrize("bad", [True, 12.5, "12"])
def test_strict_visual_save_dc(bad):
    with pytest.raises(ValueError):
        VisualTurnStartRule(source_id="source", source_name="Label", range_ft=30, save_dc=bad)

@pytest.mark.parametrize("bad", [True, 15.5, "15"])
def test_strict_distance(bad):
    with pytest.raises(ValueError):
        decide_visual_turn_start(BASILISK, _facts(distance_ft=bad))

@pytest.mark.parametrize("flag", ["source_active", "target_active", "source_sees_target",
                                  "target_sees_source", "target_immune", "target_surprised"])
def test_strict_eligibility_flags(flag):
    with pytest.raises(ValueError):
        decide_visual_turn_start(BASILISK, _facts(**{flag: 1}))

@pytest.mark.parametrize("bad", [True, False, 9.5, "9"])
def test_strict_save_totals(bad):
    with pytest.raises(ValueError):
        resolve_visual_save_stage(MEDUSA, bad)


def test_visual_save_stages_are_generic_debuffs():
    rule = VisualTurnStartRule(source_id="source", source_name="Other Trigger", range_ft=30, save_dc=12,
                               initial_debuff="slowed", terminal_debuff="stunned")
    assert resolve_visual_save_stage(rule, 3) == "slowed"
    assert resolve_visual_save_stage(rule, 3, previous_stage="slowed") == "stunned"
    assert resolve_visual_save_stage(rule, 12, previous_stage="slowed") == "clear"


def test_visual_eligibility_has_no_manual_aversion_toggle():
    # Arena AI always averts automatically unless the observer is Surprised.
    with pytest.raises(TypeError):
        VisualTurnStartFacts(**{**_facts().__dict__, "averts_eyes": False})
