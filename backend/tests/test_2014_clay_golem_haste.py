"""2014 Clay Golem Haste composed from universal timed-buff, recharge and bonus-attack primitives."""
from __future__ import annotations

from app.combat.bonus_attacks import resolve_bonus_attack_grant
from app.combat.condition_lifecycle import resolve_source_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import effective_armor_class, effective_speed
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.start_turn import begin_turn_with_events
from app.combat.state import build_combatant_state
from app.combat.timed_self_buff_policy import choose_timed_self_buff_action
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_recharge_self_buffs_2014 import (
    recharge_self_buff_bindings_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "clay-golem")
    except Exception as exc:
        raise AssertionError("Missing pinned 2014 Clay Golem") from exc


def _setup():
    source = _source()
    template = compile_combatant(adapt_basic_monster_2014(source))
    golem = EncounterCombatant(
        combatant_id="clay",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(template),
    )
    target = EncounterCombatant(
        combatant_id="target",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(
            build_demo_fighter().model_copy(update={"armor_class": 1, "max_hp": 100})
        ),
    )
    setup = EncounterSetup(
        heroes=[target],
        monsters=[golem],
        hero_total_levels=1,
        monster_total_cr=source.challenge_rating,
        ruleset="2014",
    )
    return source, setup, golem, target


def test_source_proof_binds_exact_haste_composition_without_name_dispatch():
    source = _source()
    snapshot = source.model_dump_json()
    bindings = recharge_self_buff_bindings_2014(source)

    assert len(bindings) == 1
    binding = bindings[0]
    action = binding.action
    assert (action.id, action.name, action.action_cost) == ("haste", "Haste", "action")
    assert action.resource_id == "haste"
    assert action.duration_rounds == 1
    assert action.expiry_timing == "source_turn_end"
    assert action.magical_effect is True
    assert action.concentration is False
    assert action.movement_mode_grants == []
    assert len(action.modifier_effects) == 1
    assert (action.modifier_effects[0].kind, action.modifier_effects[0].flat_bonus) == (
        "armor-class", 2,
    )
    assert action.saving_throw_advantage_grants[0].abilities == ["dexterity"]
    assert (binding.resource.id, binding.resource.max_uses) == ("haste", 1)
    assert (binding.recharge.resource_id, binding.recharge.minimum_roll) == ("haste", 5)
    assert binding.bonus_attack_grant.required_active_effect_id == "haste"
    assert binding.bonus_attack_grant.attack_count == 1
    assert basic_blockers_2014(source) == ()
    assert source.model_dump_json() == snapshot


def test_haste_spends_action_and_resource_then_grants_only_printed_benefits():
    _source_row, setup, golem, target = _setup()
    action = next(item for item in golem.state.template.timed_self_buff_actions if item.id == "haste")
    assert {item.id for item in golem.state.template.timed_self_buff_actions} >= {"haste", "berserk"}
    assert choose_timed_self_buff_action(golem, setup) == action

    base_speed = effective_speed(golem.state)
    event = resolve_timed_self_buff(
        1, 1, golem, action,
        affected_states=[golem.state, target.state], setup=setup,
    )

    resource = next(item for item in golem.state.resources if item.id == "haste")
    assert event.feature_id == "haste"
    assert event.resource_remaining == 0
    assert resource.current_uses == 0
    assert golem.state.action_available is False
    assert golem.state.bonus_action_available is True
    assert "haste" in golem.state.active_effect_ids
    assert effective_armor_class(golem.state) == golem.state.template.armor_class + 2
    assert saving_throw_mode(golem.state, "dexterity") is RollMode.ADVANTAGE
    assert saving_throw_mode(golem.state, "constitution") is RollMode.ADVANTAGE
    assert effective_speed(golem.state) == base_speed
    assert golem.state.concentration is None


def test_haste_bonus_slam_is_effect_gated_and_available_on_both_eligible_turns():
    _source_row, setup, golem, target = _setup()
    grant = next(item for item in golem.state.template.bonus_attack_grants if item.name == "Haste")
    slam = next(
        attack for attack in [golem.state.template.weapon_attack, *golem.state.template.alternate_weapon_attacks]
        if attack.id == grant.attack_ids[0]
    )
    assert slam.weapon.name == "Slam"
    assert slam.on_hit_maximum_hp_save is not None

    blocked, sequence = resolve_bonus_attack_grant(
        1, 1, golem, setup, FixedDiceProvider([10]), "1:clay",
    )
    assert blocked == [] and sequence == 1
    assert golem.state.bonus_action_available is True

    action = next(item for item in golem.state.template.timed_self_buff_actions if item.id == "haste")
    resolve_timed_self_buff(
        1, 1, golem, action,
        affected_states=[golem.state, target.state], setup=setup,
    )
    events, sequence = resolve_bonus_attack_grant(
        2, 1, golem, setup, FixedDiceProvider([10, 1, 1, 20]), "1:clay",
    )
    assert len(events) == 1
    assert events[0].feature_id == grant.id
    assert events[0].attack_name == "Slam"
    assert golem.state.bonus_action_available is False

    start_events, sequence = begin_turn_with_events(
        sequence, 2, golem.combatant_id, golem.state,
        FixedDiceProvider([4]), member=golem,
    )
    assert any(event.feature_id == "recharge:haste" for event in start_events)
    assert next(item for item in golem.state.resources if item.id == "haste").current_uses == 0
    assert "haste" in golem.state.active_effect_ids
    second, sequence = resolve_bonus_attack_grant(
        sequence, 2, golem, setup, FixedDiceProvider([10, 1, 1, 20]), "2:clay",
    )
    assert len(second) == 1 and second[0].attack_name == "Slam"


def test_haste_expires_at_end_of_next_turn_and_recharge_five_restores_it():
    _source_row, setup, golem, target = _setup()
    action = next(item for item in golem.state.template.timed_self_buff_actions if item.id == "haste")
    resolve_timed_self_buff(
        1, 1, golem, action,
        affected_states=[golem.state, target.state], setup=setup,
    )
    base_ac = golem.state.template.armor_class

    begin_turn_with_events(2, 2, golem.combatant_id, golem.state, FixedDiceProvider([4]), member=golem)
    assert "haste" in golem.state.active_effect_ids
    assert effective_armor_class(golem.state) == base_ac + 2

    ended, _ = resolve_source_condition_timing(
        3, 2, golem, setup, "source_turn_end",
    )
    assert any(event.feature_id == "haste" for event in ended)
    assert "haste" not in golem.state.active_effect_ids
    assert effective_armor_class(golem.state) == base_ac
    assert saving_throw_mode(golem.state, "dexterity") is RollMode.NORMAL

    recharge_events, _ = begin_turn_with_events(
        4, 3, golem.combatant_id, golem.state,
        FixedDiceProvider([5]), member=golem,
    )
    resource = next(item for item in golem.state.resources if item.id == "haste")
    assert resource.current_uses == 1
    assert any(
        event.feature_id == "recharge:haste" and event.resource_remaining == 1
        for event in recharge_events
    )
    fresh = build_combatant_state(golem.state.template)
    assert next(item for item in fresh.resources if item.id == "haste").current_uses == 1
    assert "haste" not in fresh.active_effect_ids
