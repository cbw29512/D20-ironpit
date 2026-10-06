from __future__ import annotations

import pytest
from unittest.mock import Mock

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import DiceProvider, FixedDiceProvider
from app.combat.source_effect_immunity import has_source_effect_immunity
from app.combat.state import build_combatant_state
from app.combat.timed_emanations import resolve_target_turn_start_emanations
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.weapons import DamageType


def _no_rolls():
    dice = Mock(spec=DiceProvider)
    dice.roll.side_effect = AssertionError("This gate must not roll dice.")
    return dice


def _setup():
    source = next(m for m in load_monster_source_2014() if m.name == "Hezrou")
    monster = compile_combatant(adapt_basic_monster_2014(source))
    target = EncounterCombatant(combatant_id="hero", side="heroes", position_ft=0,
        state=build_combatant_state(build_demo_fighter()))
    emitter = EncounterCombatant(combatant_id="source-a", side="monsters", position_ft=10,
        state=build_combatant_state(monster))
    setup = EncounterSetup(heroes=[target], monsters=[emitter], hero_total_levels=1,
        monster_total_cr="8", ruleset="2014")
    return setup, emitter, target


def test_passive_works_before_source_turn_and_poison_expires_on_target_next_start():
    setup, source, target = _setup()
    before = source.state.template.model_dump()
    events, sequence = resolve_target_turn_start_emanations(1, 1, target, setup, FixedDiceProvider([1]))
    assert len(events) == 1 and events[0].applied_condition_ids == ["poisoned"]
    assert "Stench" in events[0].description
    effect, = target.state.timed_effects
    assert (effect.expires_round, effect.expiry_timing) == (None, "target_turn_start")
    assert effect.repeat_save_dc is None and effect.repeat_save_timing is None
    assert source.state.timed_effects == [] and source.state.action_available
    # A second turn in the same round is still the target's next turn.
    ended, sequence = resolve_target_condition_timing(sequence, 1, target, "target_turn_start", _no_rolls(), setup)
    assert ended[0].removed_condition_ids == ["poisoned"]
    # Standing in the aura means another ordinary save after old Poisoned expires.
    events, _ = resolve_target_turn_start_emanations(sequence, 2, target, setup, FixedDiceProvider([20]))
    assert events[0].save_succeeded
    assert has_source_effect_immunity(target.state, "stench", source.combatant_id)
    assert source.state.template.model_dump() == before
    assert build_combatant_state(target.state.template).timed_effects == []


def test_success_immunity_is_per_source_and_match_only():
    setup, source, target = _setup()
    events, sequence = resolve_target_turn_start_emanations(1, 1, target, setup, FixedDiceProvider([20]))
    assert events[0].save_succeeded
    immunity, = target.state.timed_effects
    assert immunity.expires_round is None and immunity.expiry_timing is None
    repeated, _ = resolve_target_turn_start_emanations(sequence, 500, target, setup, _no_rolls())
    assert repeated == []
    other = source.model_copy(update={"combatant_id": "source-b", "state": build_combatant_state(source.state.template)})
    setup.monsters.append(other)
    events, _ = resolve_target_turn_start_emanations(sequence, 2, target, setup, FixedDiceProvider([1]))
    assert len(events) == 1 and events[0].actor_id == "source-b"
    assert not has_source_effect_immunity(build_combatant_state(target.state.template), "stench", source.combatant_id)


@pytest.mark.parametrize("reason", ["condition-immune", "out-of-range", "source-dead", "same-side"])
def test_gates_skip_save_and_mutation(reason):
    setup, source, target = _setup()
    if reason == "condition-immune":
        target.state.template = target.state.template.model_copy(update={"condition_immunities": ["poisoned"]})
    elif reason == "out-of-range":
        source.position_ft = 15
    elif reason == "source-dead":
        source.state.is_dead = True
        source.state.is_alive = False
    else:
        source.side = "heroes"
    events, sequence = resolve_target_turn_start_emanations(1, 1, target, setup, _no_rolls())
    assert (events, sequence) == ([], 1) and not target.state.timed_effects


def test_poison_damage_immunity_does_not_imply_condition_immunity():
    setup, _, target = _setup()
    target.state.template = target.state.template.model_copy(update={"damage_immunities": [DamageType.POISON]})
    events, _ = resolve_target_turn_start_emanations(1, 1, target, setup, FixedDiceProvider([1]))
    assert events[0].applied_condition_ids == ["poisoned"]


def test_poison_save_advantage_uses_shared_context_and_magical_defense_does_not():
    setup, _, target = _setup()
    features = target.state.template.progression_features.model_copy(deep=True)
    features.saving_throw_advantage_grants = [SavingThrowAdvantageGrant(
        source_id="poison-ward", source_name="Poison Ward", abilities=["constitution"], required_effect_tags=["poison"])]
    target.state = build_combatant_state(target.state.template.model_copy(update={"progression_features": features}))
    events, _ = resolve_target_turn_start_emanations(1, 1, target, setup, FixedDiceProvider([1, 20]))
    assert events[0].saving_throw_roll.rolls == [1, 20] and events[0].save_succeeded
    setup, _, target = _setup()
    features = target.state.template.progression_features.model_copy(deep=True)
    features.saving_throw_advantage_grants = [SavingThrowAdvantageGrant(
        source_id="magic-ward", source_name="Magic Ward", abilities=["constitution"], requires_magical_effect=True)]
    target.state = build_combatant_state(target.state.template.model_copy(update={"progression_features": features}))
    events, _ = resolve_target_turn_start_emanations(1, 1, target, setup, FixedDiceProvider([1]))
    assert events[0].saving_throw_roll.rolls == [1] and not events[0].save_succeeded


@pytest.mark.parametrize("target_x,expected_events", [(3, 1), (4, 0)])
def test_passive_range_uses_live_large_footprint(target_x, expected_events):
    setup, source, target = _setup()
    source.state.position = GridPosition(x=0, y=0)
    target.state.position = GridPosition(x=target_x, y=0)
    dice = FixedDiceProvider([1]) if expected_events else _no_rolls()
    events, _ = resolve_target_turn_start_emanations(1, 1, target, setup, dice)
    assert len(events) == expected_events
    if events:
        assert events[0].distance_before_ft == 10
