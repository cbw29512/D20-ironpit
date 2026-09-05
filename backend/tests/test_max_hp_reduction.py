from app.combat.hit_points import effective_max_hp
from app.combat.max_hp import apply_max_hp_reduction
from app.content.roster import build_arena_roster
from app.domain.models import CombatantState


def _state() -> CombatantState:
    template = next(item for item in build_arena_roster().monsters if item.name == "Commoner")
    return CombatantState(template=template, current_hp=template.max_hp)


def test_max_hp_reduction_is_shared_runtime_survival_math() -> None:
    state = _state()
    before = effective_max_hp(state)
    reduced = apply_max_hp_reduction(state, 2)
    assert reduced == min(2, before)
    assert effective_max_hp(state) == before - reduced
    assert state.current_hp == effective_max_hp(state)


def test_max_hp_reduction_stacks_against_active_max_hp_bonus() -> None:
    state = _state()
    state.max_hp_bonus = 5
    state.current_hp = effective_max_hp(state)
    assert apply_max_hp_reduction(state, 3) == 3
    assert effective_max_hp(state) == state.template.max_hp + 2


def test_max_hp_reduction_to_zero_kills_without_negative_maximum() -> None:
    state = _state()
    apply_max_hp_reduction(state, state.template.max_hp + 100)
    assert effective_max_hp(state) == 0
    assert state.current_hp == 0
    assert state.is_dead is True
    assert state.is_alive is False
