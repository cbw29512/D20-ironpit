from __future__ import annotations

import pytest

from app.combat.hit_points import effective_max_hp
from app.combat.max_hp_reduction import apply_max_hp_reduction
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter


def test_max_hp_reduction_is_runtime_only_and_clamps_current_hp() -> None:
    try:
        state = build_combatant_state(build_demo_fighter())
        printed_max = state.template.max_hp
        state.max_hp_bonus = 5
        state.current_hp = printed_max + 5

        before, after = apply_max_hp_reduction(state, 7)

        assert before == printed_max + 5
        assert after == printed_max - 2
        assert effective_max_hp(state) == printed_max - 2
        assert state.current_hp == printed_max - 2
        assert state.template.max_hp == printed_max
    except Exception:
        raise


def test_max_hp_reduction_stacks_and_never_produces_negative_effective_max() -> None:
    try:
        state = build_combatant_state(build_demo_fighter())
        apply_max_hp_reduction(state, 3)
        apply_max_hp_reduction(state, state.template.max_hp + 100)

        assert effective_max_hp(state) == 0
        assert state.current_hp == 0
        assert state.max_hp_reduction == state.template.max_hp + 103
    except Exception:
        raise


def test_max_hp_reduction_rejects_negative_amounts() -> None:
    state = build_combatant_state(build_demo_fighter())
    with pytest.raises(ValueError, match="cannot be negative"):
        apply_max_hp_reduction(state, -1)
