from __future__ import annotations

import pytest

from app.combat.ability_score_reduction import (
    apply_ability_score_reduction, effective_ability_score, effective_ability_modifier, ability_modifier_delta,
)
from app.combat.state import build_combatant_state
from app.content.monster_roster_2014 import build_basic_2014_monsters


def _state():
    template = next(x for x in build_basic_2014_monsters() if x.name == "Animated Armor")
    return build_combatant_state(template)


def test_stat_reduction_is_fight_scoped_and_changes_live_modifier() -> None:
    state = _state()
    original = effective_ability_score(state, "strength")
    reduction = apply_ability_score_reduction(state, "strength", 2, zero_kills=True)
    assert reduction.score_before == original
    assert reduction.score_after == original - 2
    assert reduction.applied == 2
    assert reduction.death_outcome is None
    assert effective_ability_modifier(state, "strength") == (original - 12) // 2
    assert state.template.ability_scores.score("strength") == original
    assert effective_ability_score(build_combatant_state(state.template), "strength") == original


def test_zero_score_is_lethal_through_existing_instant_death_lifecycle() -> None:
    state = _state()
    score = effective_ability_score(state, "strength")
    resolution = apply_ability_score_reduction(state, "strength", score, zero_kills=True)
    assert resolution.score_after == 0
    assert resolution.death_outcome == "dead"
    assert state.is_dead and state.current_hp == 0 and not state.is_alive
    assert apply_ability_score_reduction(state, "strength", 2, zero_kills=True).applied == 0


def test_any_source_reaching_zero_kills_and_invalid_inputs_fail_closed() -> None:
    state = _state()
    assert apply_ability_score_reduction(state, "strength", 999).score_after == 0
    assert state.is_dead
    state = _state()
    with pytest.raises(ValueError):
        apply_ability_score_reduction(state, "strength", -1)
    with pytest.raises(ValueError):
        apply_ability_score_reduction(state, "strength", True)
    with pytest.raises(ValueError):
        effective_ability_score(state, "bogus")


def test_a_pregen_at_zero_strength_is_dead_without_death_saves() -> None:
    base = _state().template
    hero = build_combatant_state(base.model_copy(update={"kind": "hero"}))
    amount = effective_ability_score(hero, "strength")
    outcome = apply_ability_score_reduction(hero, "strength", amount, zero_kills=True)
    assert outcome.score_after == 0
    assert outcome.death_outcome == "dead"
    assert hero.is_dead and not hero.is_unconscious and hero.current_hp == 0
    assert hero.death_save_failures == 0 and hero.death_save_successes == 0


def test_strength_loss_changes_strength_based_modifiers_not_dexterity() -> None:
    state = _state()
    assert ability_modifier_delta(state, "strength") == 0
    assert ability_modifier_delta(state, "dexterity") == 0
    apply_ability_score_reduction(state, "strength", 2)
    assert ability_modifier_delta(state, "strength") == -1
    assert ability_modifier_delta(state, "dexterity") == 0
    assert ability_modifier_delta(state, None) == 0
    assert state.template.ability_scores.strength == 14


@pytest.mark.parametrize("ability", [
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
])
@pytest.mark.parametrize("is_hero", [False, True])
def test_every_ability_zero_is_terminal_for_both_sides_and_resets(ability: str, is_hero: bool) -> None:
    template = _state().template
    if is_hero:
        template = template.model_copy(update={"kind": "hero"})
    state = build_combatant_state(template)
    original = effective_ability_score(state, ability)
    assert original > 0
    # No source-specific lethal flag: this is universal for ANY ability reduction.
    result = apply_ability_score_reduction(state, ability, original, zero_kills=False)
    assert result.score_after == 0
    assert result.death_outcome == "dead"
    assert state.is_dead and state.current_hp == 0 and not state.is_alive
    assert not state.is_unconscious
    assert state.death_save_failures == 0 and state.death_save_successes == 0
    assert template.ability_scores.score(ability) == original
    next_fight = build_combatant_state(template)
    assert effective_ability_score(next_fight, ability) == original
    assert next_fight.ability_score_reductions == {}
    assert next_fight.is_alive and not next_fight.is_dead
