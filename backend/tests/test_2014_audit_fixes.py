"""Real-state regressions for the 2014 website audit."""
import pytest
from app.combat.condition_rules import can_see
from app.combat.dice import SeededDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.hp_threshold_condition import legal_hp_threshold_condition
from app.combat.hp_threshold_instant_death import legal_hp_threshold_instant_death
from app.combat.resources import resource_state
from app.combat.spell_modifiers import apply_spell_modifiers
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import expire_start_of_turn_conditions
from app.content.shared_spells_2014 import sanctuary_2014
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def pair():
    actor = EncounterCombatant(combatant_id="actor", side="heroes", position_ft=0,
                              state=build_combatant_state(build_varek_ashenmark_2014(17)))
    target = EncounterCombatant(combatant_id="target", side="monsters", position_ft=5,
                               state=build_combatant_state(build_varek_ashenmark_2014(17)))
    actor.state.position = GridPosition(x=0, y=0)
    target.state.position = GridPosition(x=1, y=0)
    target.state.current_hp = 100
    return actor, target, EncounterSetup(heroes=[actor], monsters=[target], hero_total_levels=17,
                                        monster_total_cr="1", ruleset="2014")


@pytest.mark.parametrize("effect,owner", [("invisible", "target"), ("blinded", "actor")])
def test_threshold_requires_source_declared_visibility(effect, owner):
    actor, target, _ = pair()
    (actor if owner == "actor" else target).state.active_effect_ids.append(effect)
    assert not can_see(actor.state, target.state)
    kill = actor.state.template.hp_threshold_instant_death_actions[0]
    stun = actor.state.template.hp_threshold_condition_actions[0]
    assert kill.requires_target_sight and stun.requires_target_sight
    assert not legal_hp_threshold_instant_death(actor, target, kill)
    assert not legal_hp_threshold_condition(actor, target, stun)
    assert legal_hp_threshold_instant_death(actor, target, kill.model_copy(update={"requires_target_sight": False}))


def test_visible_threshold_boundaries_and_resource_checks():
    actor, target, _ = pair()
    kill = actor.state.template.hp_threshold_instant_death_actions[0]
    stun = actor.state.template.hp_threshold_condition_actions[0]
    assert legal_hp_threshold_instant_death(actor, target, kill)
    target.state.current_hp = 101
    assert not legal_hp_threshold_instant_death(actor, target, kill)
    target.state.current_hp = 150
    assert legal_hp_threshold_condition(actor, target, stun)
    target.state.current_hp = 151
    assert not legal_hp_threshold_condition(actor, target, stun)
    target.state.current_hp = 100
    resource_state(actor.state, kill.resource_id).current_uses = 0
    assert not legal_hp_threshold_instant_death(actor, target, kill)


@pytest.mark.parametrize("cast_round,expiry_round", [(0, 11), (3, 13)])
def test_sanctuary_source_duration_and_other_sources(cast_round, expiry_round):
    actor, target, setup = pair()
    spell = sanctuary_2014(19)
    apply_spell_modifiers(actor.state, [("target", target.state)], "actor", spell, cast_round)
    apply_spell_modifiers(actor.state, [("target", target.state)], "other", spell, cast_round)
    expire_start_of_turn_conditions(1, expiry_round - 1, actor, setup)
    assert len(target.state.active_modifiers) == 2
    expire_start_of_turn_conditions(1, expiry_round, actor, setup)
    assert [item.source_id for item in target.state.active_modifiers] == ["other"]
    assert [item.source_id for item in target.state.timed_effects] == ["other"]
    assert build_combatant_state(target.state.template).active_modifiers == []


def test_real_turn_selects_threshold_before_hex_or_cantrips():
    actor, target, setup = pair()
    events, _ = resolve_combat_turn(1, 1, actor, target, setup, SeededDiceProvider(7))
    assert any(event.feature_id == "power-word-kill" for event in events)
    assert not any(event.feature_id in {"hex", "eldritch-blast"} for event in events)
    assert target.state.is_dead
    assert resource_state(actor.state, "mystic-arcanum-9").current_uses == 0
    assert resource_state(actor.state, "spell-slot-5").current_uses == 4
