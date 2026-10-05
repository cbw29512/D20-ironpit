from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import effective_speed
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.saving_throws import resolve_save_action
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_ability_d20 import timed_ability_d20_disadvantage_sources
from app.combat.timed_attack_cap import turn_attack_allowed
from app.combat.timed_conditions import apply_timed_condition
from app.combat.exhaustion import ability_check_disadvantage_sources
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monster_save_control_2014 import (
    compile_failed_save_control_2014,
    supports_failed_save_control_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.timed_control_limits import TimedControlLimits


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _catalog_action(monster_id: str, action_id: str) -> dict:
    source = next(item for item in load_monster_source_2014() if item.id == monster_id)
    action = next(
        item for item in source.saving_throw_actions
        if isinstance(item, dict) and item.get("id") == action_id
    )
    return action


def test_2014_classifier_still_rejects_catalog_slow_and_weaken() -> None:
    slow = _catalog_action("copper-dragon-wyrmling", "slowing-breath")
    weaken = _catalog_action("gold-dragon-wyrmling", "weakening-breath")
    golem = _catalog_action("stone-golem", "slow")
    for action in (slow, weaken, golem):
        assert supports_failed_save_control_2014(action) is False
        assert compile_failed_save_control_2014(action) is None


def test_slow_rider_halves_speed_blocks_reactions_and_keeps_movement() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(5))
    apply_timed_condition(
        state,
        "slowed",
        "copper",
        source_effect_id="slowing-breath",
        suppress_reactions=True,
        control_limits=TimedControlLimits(
            speed_multiplier=0.5,
            action_bonus_exclusive=True,
            max_attacks_per_turn=1,
        ),
    )
    begin_turn(state)
    assert effective_speed(state) == 15
    assert state.movement_remaining_ft == 15
    assert is_available(state, "reaction") is False
    spend(state, "action")
    assert is_available(state, "bonus_action") is False
    assert state.movement_remaining_ft == 15


def test_single_activity_still_zeros_movement_after_an_action() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(5))
    apply_timed_condition(
        state,
        "frightened",
        "paladin",
        source_effect_id="abjure-foes",
        turn_behavior="single_activity",
    )
    begin_turn(state)
    spend(state, "action")
    assert state.movement_remaining_ft == 0
    assert is_available(state, "bonus_action") is False


def test_slow_rider_caps_extra_attack_at_one() -> None:
    hero = _member(build_karnok_stoneward_level(5), "hero-1:karnok-l5", "heroes", 0)
    target = _member(
        build_commoner().model_copy(update={"max_hp": 200, "ruleset": "2014"}),
        "monster-1",
        "monsters",
        5,
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[target], hero_total_levels=5, monster_total_cr="0", ruleset="2014",
    )
    apply_timed_condition(
        hero.state,
        "slowed",
        "copper",
        source_effect_id="slowing-breath",
        suppress_reactions=True,
        control_limits=TimedControlLimits(
            speed_multiplier=0.5,
            action_bonus_exclusive=True,
            max_attacks_per_turn=1,
        ),
    )
    begin_turn(hero.state)
    assert len(hero.state.template.attack_action.slots) == 2
    events, _ = resolve_attack_action(1, 1, hero, setup, FixedDiceProvider([2, 2, 2, 2]))
    assert len([event for event in events if event.event_type == "attack"]) == 1
    assert turn_attack_allowed(hero.state) is False


def test_failed_save_timed_rider_compiles_slow_limits() -> None:
    dragon = _member(build_commoner().model_copy(update={"ruleset": "2014"}), "dragon", "monsters", 0)
    hero = _member(build_karnok_stoneward_level(1), "hero", "heroes", 5)
    setup = EncounterSetup(
        heroes=[hero], monsters=[dragon], hero_total_levels=1, monster_total_cr="0", ruleset="2014",
    )
    del setup
    action = SavingThrowAction(
        id="slowing-breath",
        name="Slowing Breath",
        save_ability="constitution",
        dc=11,
        range_ft=15,
        failed_save_timed_effect=FailedSaveTimedEffect(
            effect_id="slowed",
            duration_rounds=10,
            expiry_timing="target_turn_end",
            repeat_save_ability="constitution",
            repeat_save_dc=11,
            repeat_save_timing="target_turn_end",
            speed_multiplier=0.5,
            blocks_reactions=True,
            action_bonus_exclusive=True,
            max_attacks_per_turn=1,
        ),
    )
    event = resolve_save_action(1, 1, dragon, hero, action, 10, FixedDiceProvider([1]))
    assert event.save_succeeded is False
    assert event.applied_condition_ids == ["slowed"]
    effect = next(item for item in hero.state.timed_effects if item.effect_id == "slowed")
    assert effect.suppress_reactions is True
    assert effect.control_limits is not None
    assert effect.control_limits.speed_multiplier == 0.5
    assert effect.control_limits.action_bonus_exclusive is True
    assert effect.control_limits.max_attacks_per_turn == 1


def test_weaken_rider_disadvantages_strength_d20_tests_only() -> None:
    state = build_combatant_state(build_karnok_stoneward_level(5))
    apply_timed_condition(
        state,
        "weakened-strength",
        "gold",
        source_effect_id="weakening-breath",
        control_limits=TimedControlLimits(d20_disadvantage_abilities=["strength"]),
    )
    assert timed_ability_d20_disadvantage_sources(state, "strength") == 1
    assert timed_ability_d20_disadvantage_sources(state, "dexterity") == 0
    assert ability_check_disadvantage_sources(state, "strength") == 1
    assert ability_check_disadvantage_sources(state, "dexterity") == 0
    assert saving_throw_mode(state, "strength") is RollMode.DISADVANTAGE
    assert saving_throw_mode(state, "dexterity") is RollMode.NORMAL
    sword = next(
        attack for attack in (state.template.weapon_attack, *state.template.alternate_weapon_attacks)
        if attack.id == "karnok-greatsword"
    )
    assert sword.attack_ability == "strength"
    bow = next(
        attack for attack in (state.template.weapon_attack, *state.template.alternate_weapon_attacks)
        if attack.id == "karnok-shortbow"
    )
    assert bow.attack_ability == "dexterity"
