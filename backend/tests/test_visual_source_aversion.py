from __future__ import annotations
import pytest
from app.combat.visual_source_aversion import (
    VisualAversionWindow, record_visual_aversion, visual_aversion_active,
    visual_source_perception, visual_aversion_attack_disadvantage,
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
                 source_precedes_target=False)
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



def test_averted_gaze_disadvantages_only_attacks_against_that_source():
    from app.combat.state import build_combatant_state
    from app.content.monster_source_2014 import load_monster_source_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.content.capability_compiler import compile_combatant
    from app.combat.attack_roll_resolution import resolve_attack_roll
    from app.combat.dice import FixedDiceProvider

    source = next(m for m in load_monster_source_2014() if m.id == "commoner")
    template = compile_combatant(adapt_basic_monster_2014(source))
    actor = build_combatant_state(template)
    defender = build_combatant_state(template)
    actor.turns_started = 1
    actor.visual_aversion_windows = list(record_visual_aversion(
        (), "observer", "gaze-a", actor.turns_started,
    ))
    attack = template.weapon_attack
    def fire(target_id, dice):
        return resolve_attack_roll(
            actor, defender, attack, 5, FixedDiceProvider(dice),
            defender_event_id=target_id, attacker_event_id="observer",
            round_number=1, turn_key="1:observer",
            advantage_sources=0, other_disadvantage_sources=0,
            close_enemy_active=False,
        ).mode
    assert fire("gaze-a", [18, 2]).value == "disadvantage"
    assert fire("gaze-b", [18]).value == "normal"
    assert fire("ally", [18]).value == "normal"
    actor.turns_started = 2
    assert visual_aversion_attack_disadvantage(
        actor.visual_aversion_windows, "observer", "gaze-a", 2,
    ) == 0
    fresh = build_combatant_state(template)
    assert fresh.visual_aversion_windows == []
    assert template.model_dump() == compile_combatant(
        adapt_basic_monster_2014(source),
    ).model_dump()
