from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.saving_throw_rolls import resolve_saving_throw, saving_throw_mode
from app.combat.state import build_combatant_state
from app.combat.turn_creature_effects import resolve_turning_saves
from app.combat.turned_creature_state import apply_turned_creature_effects
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_passive_grants_2014 import saving_throw_advantage_grants_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import RollMode
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.saving_throw_context import SavingThrowContext

TURNING = SavingThrowContext(effect_tags=frozenset({"turning"}))


def _member(name, identity, side, distance):
    source = next(m for m in load_monster_source_2014() if m.name == name)
    template = compile_combatant(adapt_basic_monster_2014(source))
    return EncounterCombatant(combatant_id=identity, side=side, position_ft=distance, state=build_combatant_state(template))


def _setup():
    source = _member("Ghast", "aura-owner", "monsters", 10)
    ghoul = _member("Ghoul", "recipient", "monsters", 30)
    other = _member("Skeleton", "other-undead", "monsters", 20)
    enemy = _member("Ghoul", "hostile-ghoul", "heroes", 0)
    setup = EncounterSetup(heroes=[enemy], monsters=[source, ghoul, other],
        hero_total_levels=1, monster_total_cr="2", ruleset="2014")
    return setup, source, ghoul, other, enemy


def _turn(setup, targets, dice):
    return resolve_turning_saves(1, 1, setup.heroes[0], setup, tuple(targets), dice,
        save_dc=14, source_effect_id="generic-turn", turned_effect_id="turned",
        resource_remaining=1, feature_name="Test Turning", include_frightened=False)


def test_passive_buff_covers_pit_eligibility_and_does_not_affect_ordinary_fear():
    setup, source, ghoul, other, enemy = _setup()
    card = source.state.template.model_dump()
    sync_friendly_save_auras(setup)
    for target in [source, ghoul, enemy]:
        assert saving_throw_mode(target.state, "wisdom", TURNING) is RollMode.ADVANTAGE
        assert saving_throw_mode(target.state, "wisdom", SavingThrowContext(condition_id="frightened", effect_tags=frozenset({"frightened"}))) is RollMode.NORMAL
    for target in [other]:
        assert saving_throw_mode(target.state, "wisdom", TURNING) is RollMode.NORMAL
    ghoul.position_ft = 100
    sync_friendly_save_auras(setup)
    assert saving_throw_mode(ghoul.state, "wisdom", TURNING) is RollMode.ADVANTAGE
    assert source.state.action_available and source.state.timed_effects == []
    assert source.state.template.model_dump() == card
    assert not build_combatant_state(ghoul.state.template).active_modifiers


def test_shared_turn_save_rolls_advantage_and_reports_printed_buff_name():
    setup, _, ghoul, _, _ = _setup()
    events, _ = _turn(setup, [ghoul], FixedDiceProvider([1, 20]))
    assert events[0].save_succeeded and events[0].saving_throw_roll.rolls == [1, 20]
    assert "Turning Defiance" in events[0].description
    ghoul.state.active_modifiers.append(CombatModifier(id="penalty", source_id="foe",
        source_effect_id="penalty", kind=ModifierKind.SAVING_THROW_DISADVANTAGE, save_ability="wisdom"))
    events, _ = _turn(setup, [ghoul], FixedDiceProvider([20]))
    assert events[0].saving_throw_roll.rolls == [20]


def test_source_destroyed_by_first_turn_save_stops_protecting_next_target():
    setup, source, ghoul, _, enemy = _setup()
    enemy.state.template = enemy.state.template.model_copy(update={"progression_features":
        enemy.state.template.progression_features.model_copy(update={"turning_failure_destroy_max_cr": "2"})})
    events, _ = _turn(setup, [source, ghoul], FixedDiceProvider([1, 1, 20]))
    assert source.state.is_dead and events[0].saving_throw_roll.rolls == [1, 1]
    assert events[1].saving_throw_roll.rolls == [20]
    assert "Turning Defiance" not in events[1].description


def test_lich_self_buff_uses_existing_passive_modifier_and_shared_cancellation():
    lich = next(m for m in load_monster_source_2014() if m.name == "Lich")
    template = build_commoner().model_copy(update={"ruleset": "2014", "progression_features":
        build_commoner().progression_features.model_copy(update={"saving_throw_advantage_grants": saving_throw_advantage_grants_2014(lich)})})
    state = build_combatant_state(template)
    roll, _ = resolve_saving_throw(state, "wisdom", 14, FixedDiceProvider([1, 20]), TURNING)
    assert roll.rolls == [1, 20]
    assert any(item.source_name == "Turn Resistance" for item in state.active_modifiers)
    assert saving_throw_mode(state, "wisdom", SavingThrowContext()) is RollMode.NORMAL
    assert len(build_combatant_state(state.template).active_modifiers) == len(state.active_modifiers)


@pytest.mark.parametrize("source_dead,rolls", [(False, [1, 20]), (True, [20])])
def test_turn_repeat_save_retains_context_and_refreshes_live_aura(source_dead, rolls):
    setup, source, ghoul, _, enemy = _setup()
    apply_turned_creature_effects(enemy, ghoul, setup, 1,
        source_effect_id="test-turn", turned_effect_id="trembling",
        include_frightened=False, include_incapacitated=False,
        repeat_save_ability="wisdom", repeat_save_dc=14, repeat_save_timing="target_turn_end")
    sync_friendly_save_auras(setup)
    source.state.is_dead = source_dead
    events, _ = resolve_target_condition_timing(1, 1, ghoul, "target_turn_end", FixedDiceProvider(rolls), setup)
    assert events[0].saving_throw_roll.rolls == rolls
    assert ("Turning Defiance" in events[0].description) is not source_dead
    assert events[0].removed_condition_ids == ["trembling"]


@pytest.mark.parametrize("x,mode", [(7, RollMode.ADVANTAGE), (8, RollMode.NORMAL)])
def test_aura_distance_uses_live_large_footprints(x, mode):
    setup, source, ghoul, _, _ = _setup()
    actions = [action.model_copy(update={"friendly_save_advantage_aura": action.friendly_save_advantage_aura.model_copy(update={"covers_arena": False})})
        if action.friendly_save_advantage_aura else action for action in source.state.template.timed_self_buff_actions]
    source.state.template = source.state.template.model_copy(update={"size": "large", "timed_self_buff_actions": actions})
    source.state.position = GridPosition(x=0, y=0)
    ghoul.state.position = GridPosition(x=x, y=0)
    setup.monsters = [source, ghoul]
    setup.heroes = []
    sync_friendly_save_auras(setup)
    assert saving_throw_mode(ghoul.state, "wisdom", TURNING) is mode
