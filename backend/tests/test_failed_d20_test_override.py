from __future__ import annotations

from app.combat.failed_d20_test_override import apply_failed_d20_test_override
from app.combat.ability_checks import resolve_ability_check_outcome
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.audited_rogue import build_mara_quickstep_level
from app.combat.dice import FixedDiceProvider
from app.domain.models import DiceRoll, RollMode


def test_failed_d20_override_replaces_selected_die_and_spends_resource() -> None:
    state = build_combatant_state(build_mara_quickstep_level(20))
    original = DiceRoll(
        notation="1d20+11", rolls=[4], selected_roll=4,
        modifier=11, total=15, mode=RollMode.NORMAL,
    )

    revised, feature_id, source_name = apply_failed_d20_test_override(
        state, original, failed=True, test_kind="attack",
    )

    assert revised is not None
    assert revised.selected_roll == 20
    assert revised.total == 31
    assert revised.revisions[-1].kind == "die_replacement"
    assert revised.revisions[-1].source_effect_id == "stroke-of-luck"
    assert revised.revisions[-1].original_selected == 4
    assert revised.revisions[-1].replacement_selected == 20
    assert feature_id == "stroke-of-luck"
    assert source_name == "Stroke of Luck"
    assert next(item for item in state.resources if item.id == "stroke-of-luck").current_uses == 0


def test_failed_save_uses_same_universal_d20_override() -> None:
    state = build_combatant_state(build_mara_quickstep_level(20))

    roll, succeeded = resolve_saving_throw(
        state, "wisdom", 20, FixedDiceProvider([1]),
    )

    assert roll is not None
    assert roll.selected_roll == 20
    assert roll.total == 27
    assert succeeded is True
    assert roll.revisions[-1].source_effect_id == "stroke-of-luck"
    assert next(item for item in state.resources if item.id == "stroke-of-luck").current_uses == 0


def test_failed_d20_override_does_not_spend_on_success_or_ineligible_test() -> None:
    state = build_combatant_state(build_mara_quickstep_level(20))
    roll = DiceRoll(
        notation="1d20+11", rolls=[12], selected_roll=12,
        modifier=11, total=23, mode=RollMode.NORMAL,
    )

    unchanged, feature_id, _ = apply_failed_d20_test_override(
        state, roll, failed=False, test_kind="attack",
    )

    assert unchanged == roll
    assert feature_id is None
    assert next(item for item in state.resources if item.id == "stroke-of-luck").current_uses == 1


def test_failed_ability_check_uses_same_universal_d20_override() -> None:
    state = build_combatant_state(build_mara_quickstep_level(20))
    original = DiceRoll(
        notation="1d20+2", rolls=[3], selected_roll=3,
        modifier=2, total=5, mode=RollMode.NORMAL,
    )

    revised, succeeded = resolve_ability_check_outcome(
        state, "strength", original, 20,
    )

    assert revised.selected_roll == 20
    assert revised.total == 22
    assert succeeded is True
    assert revised.revisions[-1].source_effect_id == "stroke-of-luck"
    assert next(item for item in state.resources if item.id == "stroke-of-luck").current_uses == 0
