from __future__ import annotations

import pytest

from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.domain.models import ConditionRemovalAction, EncounterSelection, ResourceState, TimedEffect


def _setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-commoner"],
        starting_distance_ft=5,
    ))
    return setup, setup.heroes[0], setup.heroes[1]


def _turn_key(round_number, member) -> str:
    return f"{round_number}:{member.combatant_id}"


def test_lay_on_hands_poison_removal_spends_bonus_action_and_five_pool_points() -> None:
    setup, paladin, ally = _setup()
    paladin.state.template.condition_removal_actions = [ConditionRemovalAction(
        id="lay-on-hands-poison",
        name="Lay on Hands",
        action_cost="bonus_action",
        range_ft=5,
        removable_conditions=["poisoned"],
        resource_costs_per_condition={"lay-on-hands": 5},
    )]
    paladin.state.resources.append(ResourceState(id="lay-on-hands", name="Lay on Hands", current_uses=5, max_uses=5))
    ally.state.active_effect_ids.append("poisoned")
    ally.state.timed_effects.append(TimedEffect(effect_id="poisoned", source_id="monster-1", expires_at_start_of_source_turn=True))
    turn_key = _turn_key(1, paladin)

    choice = choose_condition_removal_action(paladin, setup, turn_key)
    assert choice is not None
    action, target, conditions = choice
    assert target is ally
    assert conditions == ["poisoned"]

    event = resolve_condition_removal(1, 1, paladin, target, action, conditions, turn_key)
    assert paladin.state.bonus_action_available is False
    assert next(item for item in paladin.state.resources if item.id == "lay-on-hands").current_uses == 0
    assert "poisoned" not in ally.state.active_effect_ids
    assert ally.state.timed_effects == []
    assert event.removed_condition_ids == ["poisoned"]


def test_lesser_restoration_removes_one_legal_condition_and_spends_one_slot() -> None:
    setup, cleric, ally = _setup()
    cleric.state.template.condition_removal_actions = [ConditionRemovalAction(
        id="lesser-restoration",
        name="Lesser Restoration",
        action_cost="bonus_action",
        range_ft=5,
        removable_conditions=["blinded", "deafened", "paralyzed", "poisoned"],
        max_conditions_per_use=1,
        resource_costs={"spell-slot-2": 1},
        expends_spell_slot=True,
    )]
    cleric.state.resources.append(ResourceState(id="spell-slot-2", name="2nd-level Spell Slot", current_uses=1, max_uses=1))
    ally.state.active_effect_ids.extend(["poisoned", "paralyzed"])
    turn_key = _turn_key(1, cleric)

    choice = choose_condition_removal_action(cleric, setup, turn_key)
    assert choice is not None
    action, target, conditions = choice
    assert target is ally
    assert conditions == ["paralyzed"], "AI should clear the more debilitating legal condition first"

    resolve_condition_removal(1, 1, cleric, target, action, conditions, turn_key)
    assert "paralyzed" not in ally.state.active_effect_ids
    assert "poisoned" in ally.state.active_effect_ids
    assert next(item for item in cleric.state.resources if item.id == "spell-slot-2").current_uses == 0
    assert cleric.state.spell_slot_expended_turn_key == turn_key


def test_2024_second_slot_spell_is_blocked_until_a_different_turn() -> None:
    setup, caster, ally = _setup()
    caster.state.template.condition_removal_actions = [
        ConditionRemovalAction(
            id="lesser-restoration",
            name="Lesser Restoration",
            action_cost="bonus_action",
            removable_conditions=["paralyzed"],
            resource_costs={"spell-slot-2": 1},
            expends_spell_slot=True,
        ),
        ConditionRemovalAction(
            id="test-action-slot-spell",
            name="Test Action Slot Spell",
            action_cost="action",
            removable_conditions=["blinded"],
            resource_costs={"spell-slot-3": 1},
            expends_spell_slot=True,
        ),
    ]
    caster.state.resources.extend([
        ResourceState(id="spell-slot-2", name="2nd-level Spell Slot", current_uses=1, max_uses=1),
        ResourceState(id="spell-slot-3", name="3rd-level Spell Slot", current_uses=1, max_uses=1),
    ])
    ally.state.active_effect_ids.extend(["paralyzed", "blinded"])
    first_turn = _turn_key(1, caster)
    action, target, conditions = choose_condition_removal_action(caster, setup, first_turn)
    resolve_condition_removal(1, 1, caster, target, action, conditions, first_turn)

    assert caster.state.action_available is True, "The slot rule must matter independently of Action availability"
    assert choose_condition_removal_action(caster, setup, first_turn) is None

    begin_turn(caster.state)
    second_turn = _turn_key(2, caster)
    choice = choose_condition_removal_action(caster, setup, second_turn)
    assert choice is not None
    assert choice[0].id == "test-action-slot-spell"


def test_effect_specific_removal_restriction_fails_closed() -> None:
    setup, remover, ally = _setup()
    remover.state.template.condition_removal_actions = [ConditionRemovalAction(
        id="generic-cleanse",
        name="Generic Cleanse",
        action_cost="bonus_action",
        removable_conditions=["poisoned"],
    )]
    ally.state.active_effect_ids.append("poisoned")
    ally.state.timed_effects.append(TimedEffect(
        effect_id="poisoned",
        source_id="restricted-source",
        allowed_removal_action_ids=["specific-cleanse"],
    ))
    assert choose_condition_removal_action(remover, setup, _turn_key(1, remover)) is None


def test_lesser_restoration_does_not_remove_stunned_in_2024() -> None:
    setup, cleric, ally = _setup()
    cleric.state.template.condition_removal_actions = [ConditionRemovalAction(
        id="lesser-restoration",
        name="Lesser Restoration",
        action_cost="bonus_action",
        removable_conditions=["blinded", "deafened", "paralyzed", "poisoned"],
    )]
    ally.state.active_effect_ids.append("stunned")
    assert choose_condition_removal_action(cleric, setup, _turn_key(1, cleric)) is None


def test_reaction_removal_requires_explicit_trigger_and_is_not_used_on_turn() -> None:
    with pytest.raises(ValueError):
        ConditionRemovalAction(
            id="bad-reaction",
            name="Bad Reaction",
            action_cost="reaction",
            removable_conditions=["poisoned"],
        )

    setup, remover, ally = _setup()
    remover.state.template.condition_removal_actions = [ConditionRemovalAction(
        id="triggered-cleanse",
        name="Triggered Cleanse",
        action_cost="reaction",
        removable_conditions=["poisoned"],
        reaction_trigger="condition_applied_to_ally",
    )]
    ally.state.active_effect_ids.append("poisoned")
    assert choose_condition_removal_action(remover, setup, _turn_key(1, remover)) is None
