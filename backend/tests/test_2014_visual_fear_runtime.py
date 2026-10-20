"""2014 source-proven passive fear uses the same visual/timed primitives as other cards."""
from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.capability_compiler import compile_combatant
from app.combat.state import build_combatant_state
from app.combat.turn_start_visual_effects import resolve_visual_turn_start_events
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup():
    monsters = {row.id: row for row in load_monster_source_2014()}
    sea = monsters["sea-hag"]
    sea_before = sea.model_dump_json()
    rule = visual_turn_start_rule_2014(sea)
    assert rule is not None and rule.failed_save_timed_effect is not None
    assert (rule.range_ft, rule.save_dc, rule.save_ability) == (30, 11, "wisdom")
    assert rule.required_target_creature_types == ["humanoid"]
    assert (rule.failed_save_timed_effect.effect_id,
            rule.failed_save_timed_effect.duration_rounds) == ("frightened", 10)
    assert sea.model_dump_json() == sea_before

    template = compile_combatant(adapt_basic_monster_2014(monsters["commoner"]))
    source = EncounterCombatant(combatant_id="source", side="monsters",
        position_ft=10, state=build_combatant_state(
            template.model_copy(update={"visual_turn_start_rule": rule})))
    target = EncounterCombatant(combatant_id="target", side="heroes",
        position_ft=0, state=build_combatant_state(template))
    target.state.turns_started = 1
    setup = EncounterSetup(heroes=[target], monsters=[source],
        ruleset="2014", hero_total_levels=0, monster_total_cr="0")
    return setup, source, target, rule


def test_visual_fear_applies_shared_frightened_repeat_save_then_source_immunity():
    setup, source, target, rule = _setup()
    events, seq = resolve_visual_turn_start_events(
        1, 1, target, setup, FixedDiceProvider([1]), ["source", "target"])
    assert len(events) == 1 and not events[0].save_succeeded
    assert events[0].applied_condition_ids == ["frightened"]
    assert target.state.timed_effects[0].repeat_save_timing == "target_turn_end"
    assert target.state.timed_effects[0].repeat_save_disadvantage_while_source_visible
    recovered, _ = resolve_target_condition_timing(
        seq, 1, target, "target_turn_end", FixedDiceProvider([20, 20]), setup)
    assert recovered and recovered[0].save_succeeded
    assert "frightened" not in target.state.active_effect_ids
    assert has_source_effect_immunity(target.state, rule.source_id, source.combatant_id)
    again, _ = resolve_visual_turn_start_events(
        20, 2, target, setup, FixedDiceProvider([1]), ["source", "target"])
    assert again == []


def test_visual_fear_aversion_true_form_and_target_type_qualifiers():
    setup, source, target, _ = _setup()
    averted, _ = resolve_visual_turn_start_events(
        1, 1, target, setup, FixedDiceProvider([1]), ["target", "source"])
    assert len(averted) == 1 and averted[0].event_type == "feature"
    assert target.state.visual_aversion_windows
    setup, source, target, _ = _setup()
    source.state.true_form_visible = False
    absent, _ = resolve_visual_turn_start_events(
        1, 1, target, setup, FixedDiceProvider([1]), ["source", "target"])
    assert absent == []
    setup, source, target, _ = _setup()
    other = target.state.template.model_copy(update={"creature_type": "undead"})
    target.state.template = other
    blocked, _ = resolve_visual_turn_start_events(
        1, 1, target, setup, FixedDiceProvider([1]), ["source", "target"])
    assert blocked == []


def test_initial_success_grants_only_that_source_immunity():
    setup, source, target, rule = _setup()
    success, _ = resolve_visual_turn_start_events(
        1, 1, target, setup, FixedDiceProvider([20]), ["source", "target"])
    assert success[0].save_succeeded and success[0].applied_condition_ids == []
    assert has_source_effect_immunity(target.state, rule.source_id, "source")
    assert not has_source_effect_immunity(target.state, rule.source_id, "another-source")
