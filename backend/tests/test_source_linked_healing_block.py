"""Generic source-linked timed effect preventing HP recovery (2014 Beard prerequisite)."""

from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.combat.zero_hp import restore_hit_points
from app.content.monsters_low_cr import build_giant_rat


def _target():
    state = build_combatant_state(build_giant_rat())
    state.current_hp = 1
    return state


def test_source_linked_no_healing_blocks_only_while_effect_is_present() -> None:
    state = _target()
    applied = apply_timed_condition(
        state, "poisoned", "source-a", source_effect_id="Beard",
        cannot_regain_hit_points=True, use_default_poison_recovery=False,
        expires_at_start_of_source_turn=False, expiry_timing="target_turn_end",
        repeat_save_ability="constitution", repeat_save_dc=12,
        repeat_save_timing="target_turn_end", applied_round=1, expires_round=11,
    )
    assert applied == "poisoned"
    assert len(state.timed_effects) == 1
    assert state.timed_effects[0].cannot_regain_hit_points
    assert restore_hit_points(state, 9) == 0
    assert state.current_hp == 1

    effect = state.timed_effects[0]
    assert remove_effect_instance(state, effect)
    assert restore_hit_points(state, 9) == min(9, state.template.max_hp - 1)
    assert state.current_hp == state.template.max_hp


def test_independent_poisoned_instances_do_not_inherit_heal_block() -> None:
    state = _target()
    apply_timed_condition(
        state, "poisoned", "source-a", source_effect_id="Beard",
        cannot_regain_hit_points=True, use_default_poison_recovery=False,
        expires_at_start_of_source_turn=False,
    )
    apply_timed_condition(
        state, "poisoned", "source-b", source_effect_id="ordinary-poison",
        use_default_poison_recovery=False, expires_at_start_of_source_turn=False,
    )
    assert len(state.timed_effects) == 2
    assert restore_hit_points(state, 5) == 0
    blocked = next(e for e in state.timed_effects if e.source_id == "source-a")
    remove_effect_instance(state, blocked)
    assert "poisoned" in state.active_effect_ids
    assert restore_hit_points(state, 5) == 5


def test_generic_recovery_block_does_not_require_poisoned() -> None:
    state = _target()
    apply_timed_condition(
        state, "frightened", "other-source", source_effect_id="curse",
        cannot_regain_hit_points=True, expires_at_start_of_source_turn=False,
    )
    assert restore_hit_points(state, 3) == 0
    assert state.current_hp == 1
