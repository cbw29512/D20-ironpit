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


def _production_selection() -> EncounterSelection:
    return EncounterSelection(
        ruleset="2014",
        hero_ids=["karnok-stoneward-2014-l5"],
        monster_ids=["2014-unicorn", "2014-berserker"],
    )


def _harness_selection() -> EncounterSelection:
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


def _setup(selection: EncounterSelection):
    setup = build_encounter_setup(selection)
    return setup, setup.monsters[0], setup.monsters[1], setup.heroes[0]


def test_player_loaded_legendary_matchup_starts_without_a_debuff() -> None:
    setup, unicorn, ally, _hero = _setup(_production_selection())
    assert ally.state.timed_effects == []
    assert "frightened" not in ally.state.active_effect_ids
    assert "charmed" not in ally.state.active_effect_ids
    assert unicorn.state.timed_effects == []


def test_harness_may_seed_fear_so_calm_can_be_asserted() -> None:
    setup, unicorn, ally, hero = _setup(_harness_selection())
    assert "frightened" in ally.state.active_effect_ids
    assert has_condition(ally.state, "frightened") is True
    assert ally.state.timed_effects[0].source_id == hero.combatant_id
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


def test_turn_start_reads_harness_fear_before_the_creature_acts() -> None:
    setup, _unicorn, ally, _hero = _setup(_harness_selection())
    events, _ = begin_turn_with_events(1, 1, ally.combatant_id, ally.state, FixedDiceProvider([10]), member=ally)
    assert any(
        event.feature_id == "turn-start-condition" and event.applied_condition_ids == ["frightened"]
        for event in events
    )


def test_support_phase_casts_the_answering_buff_when_a_friend_is_frightened() -> None:
    setup, unicorn, ally, _hero = _setup(_harness_selection())
    begin_turn_with_events(1, 1, unicorn.combatant_id, unicorn.state, FixedDiceProvider([10]), member=unicorn)
    events, _ = resolve_support_actions(1, 1, unicorn, setup, FixedDiceProvider([1] * 8), "1:unicorn")
    assert any(event.feature_id == "calm-emotions" for event in events)
    assert has_condition(ally.state, "frightened") is False


def test_no_counter_cast_when_nobody_has_the_matching_debuff() -> None:
    setup, unicorn, _ally, _hero = _setup(_production_selection())
    begin_turn_with_events(1, 1, unicorn.combatant_id, unicorn.state, FixedDiceProvider([10]), member=unicorn)
    assert choose_condition_counter_spell(unicorn, setup, "1:unicorn") is None


def test_bloodied_is_the_need_that_healing_answers() -> None:
    setup, _unicorn, ally, _hero = _setup(_production_selection())
    ally.state.current_hp = max(1, ally.state.template.max_hp // 2)
    assert is_bloodied(ally.state) is True
    events, _ = begin_turn_with_events(1, 1, ally.combatant_id, ally.state, FixedDiceProvider([10]), member=ally)
    assert any(event.feature_id == "turn-start-bloodied" for event in events)
