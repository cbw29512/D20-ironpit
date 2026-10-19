from __future__ import annotations
import pytest
from app.combat.visual_source_aversion import (
    VisualAversionWindow, record_visual_aversion, visual_aversion_active,
    visual_source_perception,
)
from app.combat.turn_start_visual_policy import (
    VisualTurnStartRule, VisualTurnStartFacts, decide_visual_turn_start,
)

def test_source_scoped_aversion_lifecycle_and_fight_reset():
    first = record_visual_aversion((), "observer", "source-a", 1)
    assert visual_aversion_active(first, "observer", "source-a", 1)
    assert not visual_aversion_active(first, "observer", "source-b", 1)
    assert not visual_aversion_active(first, "observer", "source-a", 2)
    assert not visual_aversion_active((), "observer", "source-a", 1)
    second = record_visual_aversion(first, "observer", "source-b", 1)
    assert len(second) == 2 and len(first) == 1
    third = record_visual_aversion(second, "observer", "source-a", 2)
    assert len(third) == 1 and third[0].expires_on_observer_turn_start == 3

def test_nonvisual_sense_does_not_trigger_gaze():
    windows = record_visual_aversion((), "observer", "source-a", 1)
    visual, perceived = visual_source_perception(
        windows, "observer", "source-a", 1, visual_sight=True, nonvisual_perception=True)
    assert not visual and perceived
    assert visual_source_perception(windows, "observer", "source-b", 1,
                                    visual_sight=True, nonvisual_perception=False) == (True, True)
    rule = VisualTurnStartRule(source_id="source-trait", source_name="Printed Name", range_ft=30, save_dc=12)
    facts = dict(distance_ft=15, source_active=True, target_active=True,
                 source_sees_target=True, target_immune=False,
                 target_surprised=False)
    assert decide_visual_turn_start(rule, VisualTurnStartFacts(
        **facts, target_sees_source=visual)) == "ineligible"
    assert decide_visual_turn_start(rule, VisualTurnStartFacts(
        **facts, target_sees_source=True)) == "averted"

@pytest.mark.parametrize("observer,source,turn", [
    ("", "source", 1), ("observer", "", 1), (5, "source", 1),
    ("observer", "source", True), ("observer", "source", -1),
])
def test_invalid_identity_and_turn_fail_closed(observer, source, turn):
    with pytest.raises(ValueError):
        record_visual_aversion((), observer, source, turn)

def test_corrupt_fight_state_rejected_even_when_sight_absent():
    corrupt = (VisualAversionWindow("observer", "source", -1),)
    with pytest.raises(ValueError):
        visual_source_perception(corrupt, "observer", "source", 1,
                                 visual_sight=False, nonvisual_perception=True)
    with pytest.raises(ValueError):
        visual_aversion_active(corrupt, "observer", "source", 1)
    with pytest.raises(ValueError):
        visual_source_perception((), "observer", "source", 1,
                                 visual_sight=1, nonvisual_perception=False)
