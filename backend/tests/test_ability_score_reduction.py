from __future__ import annotations

import pytest

from app.combat.ability_score_reduction import (
    apply_ability_score_reduction, effective_ability_score, effective_ability_modifier,
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


def test_nonlethal_source_caps_reduction_and_invalid_inputs_fail_closed() -> None:
    state = _state()
    score = effective_ability_score(state, "strength")
    assert apply_ability_score_reduction(state, "strength", 999).score_after == 1
    assert not state.is_dead
    with pytest.raises(ValueError):
        apply_ability_score_reduction(state, "strength", -1)
    with pytest.raises(ValueError):
        apply_ability_score_reduction(state, "strength", True)
    with pytest.raises(ValueError):
        effective_ability_score(state, "bogus")
