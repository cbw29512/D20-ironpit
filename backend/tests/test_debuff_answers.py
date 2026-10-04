from app.combat.bloodied import is_bloodied
from app.combat.condition_counter_policy import choose_condition_counter_spell
from app.combat.condition_rules import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_turn_support import resolve_support_actions
from app.combat.spell_resolution import resolve_spell
from app.combat.start_turn import begin_turn_with_events
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterSelection, OpeningConditionBinding


def _selection() -> EncounterSelection:
    return EncounterSelection(
        ruleset="2014",
        hero_ids=["karnok-stoneward-2014-l5"],
        monster_ids=["2014-unicorn", "2014-berserker"],
        opening_conditions=[
            OpeningConditionBinding(
                side="monsters",
                roster_index=2,
                condition_id="frightened",
                source_side="heroes",
                source_roster_index=1,
            ),
        ],
    )


def _setup():
    setup = build_encounter_setup(_selection())
    unicorn = setup.monsters[0]
    ally = setup.monsters[1]
    hero = setup.heroes[0]
    return setup, unicorn, ally, hero


def test_opening_condition_applies_fear_to_the_named_roster_slot() -> None:
    setup, _unicorn, ally, hero = _setup()
    assert "frightened" in ally.state.active_effect_ids
    assert has_condition(ally.state, "frightened") is True
    assert ally.state.timed_effects[0].source_id == hero.combatant_id
    assert "frightened" not in setup.monsters[0].state.active_effect_ids


def test_turn_start_reads_active_fear_before_the_creature_acts() -> None:
    setup, _unicorn, ally, _hero = _setup()
    events, _ = begin_turn_with_events(1, 1, ally.combatant_id, ally.state, FixedDiceProvider([10]), member=ally)
    assert any(
        event.feature_id == "turn-start-condition" and event.applied_condition_ids == ["frightened"]
        for event in events
    )


def test_condition_counter_buff_answers_live_fear_and_blocks_a_new_copy() -> None:
    setup, unicorn, ally, hero = _setup()
    begin_turn_with_events(1, 1, unicorn.combatant_id, unicorn.state, FixedDiceProvider([10]), member=unicorn)
    choice = choose_condition_counter_spell(unicorn, setup, "1:unicorn")
    assert choice is not None
    assert choice.action.id == "calm-emotions"
    assert ally.combatant_id in choice.target_ids
    events, _ = resolve_spell(1, 1, unicorn, setup, choice, "1:unicorn", FixedDiceProvider([1] * 8))
    assert any(event.feature_id == "calm-emotions" for event in events)
    assert "frightened" in ally.state.active_effect_ids
    assert has_condition(ally.state, "frightened") is False
    assert apply_timed_condition(ally.state, "frightened", hero.combatant_id, source_is_magical=True) is None
    assert has_condition(ally.state, "frightened") is False


def test_support_phase_casts_the_answering_buff_when_a_friend_is_frightened() -> None:
    setup, unicorn, ally, _hero = _setup()
    begin_turn_with_events(1, 1, unicorn.combatant_id, unicorn.state, FixedDiceProvider([10]), member=unicorn)
    events, _ = resolve_support_actions(1, 1, unicorn, setup, FixedDiceProvider([1] * 8), "1:unicorn")
    assert any(event.feature_id == "calm-emotions" for event in events)
    assert has_condition(ally.state, "frightened") is False


def test_no_counter_cast_when_nobody_has_the_matching_debuff() -> None:
    setup = build_encounter_setup(EncounterSelection(
        ruleset="2014",
        hero_ids=["karnok-stoneward-2014-l5"],
        monster_ids=["2014-unicorn", "2014-berserker"],
    ))
    unicorn = setup.monsters[0]
    begin_turn_with_events(1, 1, unicorn.combatant_id, unicorn.state, FixedDiceProvider([10]), member=unicorn)
    assert choose_condition_counter_spell(unicorn, setup, "1:unicorn") is None


def test_bloodied_is_the_need_that_healing_answers() -> None:
    setup, _unicorn, ally, _hero = _setup()
    ally.state.current_hp = max(1, ally.state.template.max_hp // 2)
    assert is_bloodied(ally.state) is True
    events, _ = begin_turn_with_events(1, 1, ally.combatant_id, ally.state, FixedDiceProvider([10]), member=ally)
    assert any(event.feature_id == "turn-start-bloodied" for event in events)
