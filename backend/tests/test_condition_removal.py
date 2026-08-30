from __future__ import annotations

import pytest

from app.combat.condition_removal import choose_condition_removal_action, resolve_condition_removal
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import ConditionRemovalAction, EncounterSelection, ResourceState, TimedEffect


def _setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-commoner"],
        starting_distance_ft=5,
    ))
    return setup, setup.heroes[0], setup.heroes[1]


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

    choice = choose_condition_removal_action(paladin, setup)
    assert choice is not None
    action, target, conditions = choice
    assert target is ally
    assert conditions == ["poisoned"]

    event = resolve_condition_removal(1, 1, paladin, target, action, conditions)
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
    )]
    cleric.state.resources.append(ResourceState(id="spell-slot-2", name="2nd-level Spell Slot", current_uses=1, max_uses=1))
    ally.state.active_effect_ids.extend(["poisoned", "paralyzed"])

    choice = choose_condition_removal_action(cleric, setup)
    assert choice is not None
    action, target, conditions = choice
    assert target is ally
    assert conditions == ["paralyzed"], "AI should clear the more debilitating legal condition first"

    resolve_condition_removal(1, 1, cleric, target, action, conditions)
    assert "paralyzed" not in ally.state.active_effect_ids
    assert "poisoned" in ally.state.active_effect_ids
    assert next(item for item in cleric.state.resources if item.id == "spell-slot-2").current_uses == 0


def test_lesser_restoration_does_not_remove_stunned_in_2024() -> None:
    setup, cleric, ally = _setup()
    cleric.state.template.condition_removal_actions = [ConditionRemovalAction(
        id="lesser-restoration",
        name="Lesser Restoration",
        action_cost="bonus_action",
        removable_conditions=["blinded", "deafened", "paralyzed", "poisoned"],
    )]
    ally.state.active_effect_ids.append("stunned")
    assert choose_condition_removal_action(cleric, setup) is None


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
    assert choose_condition_removal_action(remover, setup) is None
