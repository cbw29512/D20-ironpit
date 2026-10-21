"""Universal card-owned Investigation checks against visual disguises."""
from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.state import build_combatant_state
from app.combat.visual_disguise import resolve_visual_disguise_inspection
from app.domain.visual_disguise import VisualDisguiseAction
from test_2014_visual_disguise_opening import _setup


def _battle(*, score=10, skill_bonus=4, dc=16, cost="action"):
    setup, source, observer = _setup()
    original = observer.state.template
    declared = source.state.template.visual_disguise_action
    source.state.template = source.state.template.model_copy(update={
        "visual_disguise_action": VisualDisguiseAction.model_validate(
            declared.model_dump() | {"inspection_dc": dc, "inspection_cost": cost},
        ),
    })
    observer.state.template = original.model_copy(update={
        "kind": "character",
        "ability_scores": original.ability_scores.model_copy(update={"intelligence": score}),
        "skill_bonuses": {"investigation": skill_bonus},
    })
    prepare_opening_buffs(setup)
    assert source.state.magical_visual_disguise_active
    return setup, source, observer


def test_skill_and_proficiency_from_card_exact_dc_and_action_cost():
    setup, source, observer = _battle()
    original_source = source.state.template.model_dump_json()
    event = resolve_visual_disguise_inspection(
        1, 1, observer, source, FixedDiceProvider([12]), setup)
    assert event.check_ability == "intelligence (investigation)"
    assert event.check_dc == 16
    assert event.ability_check_roll.total == 16
    assert event.check_succeeded is True
    assert observer.state.action_available is False
    assert observer.state.bonus_action_available is True
    assert observer.state.recognized_visual_disguise_source_ids == ["source"]
    assert source.state.magical_visual_disguise_active is True
    assert source.state.true_form_visible is True
    assert original_source == source.state.template.model_dump_json()
    assert build_combatant_state(observer.state.template).recognized_visual_disguise_source_ids == []


def test_failure_spends_action_and_does_not_expose_real_form():
    setup, source, observer = _battle()
    event = resolve_visual_disguise_inspection(
        1, 1, observer, source, FixedDiceProvider([11]), setup)
    assert event.check_succeeded is False and event.ability_check_roll.total == 15
    assert observer.state.action_available is False
    assert observer.state.recognized_visual_disguise_source_ids == []
    assert source.state.magical_visual_disguise_active
    with pytest.raises(ValueError, match="unavailable"):
        resolve_visual_disguise_inspection(
            2, 1, observer, source, FixedDiceProvider([20]), setup)


def test_renamed_pregen_and_changed_card_dc_use_identical_mechanic():
    setup, source, observer = _battle(dc=18)
    source.state.template = source.state.template.model_copy(update={"name": "Masked Pregen"})
    source.state.template = source.state.template.model_copy(update={"kind": "character"})
    failure = resolve_visual_disguise_inspection(
        1, 1, observer, source, FixedDiceProvider([12]), setup)
    assert failure.check_dc == 18 and failure.ability_check_roll.total == 16
    assert failure.check_succeeded is False


def test_natural_one_and_twenty_are_not_automatic_ability_check_outcomes():
    setup, source, observer = _battle(skill_bonus=16)
    succeeded = resolve_visual_disguise_inspection(
        1, 1, observer, source, FixedDiceProvider([1]), setup)
    assert succeeded.ability_check_roll.selected_roll == 1
    assert succeeded.check_succeeded
    setup, source, observer = _battle(skill_bonus=-10)
    failed = resolve_visual_disguise_inspection(
        1, 1, observer, source, FixedDiceProvider([20]), setup)
    assert failed.ability_check_roll.selected_roll == 20
    assert failed.ability_check_roll.total == 10
    assert failed.check_succeeded is False


def test_printed_bonus_action_inspection_uses_only_bonus_action():
    setup, source, observer = _battle(cost="bonus_action", dc=19)
    event = resolve_visual_disguise_inspection(
        1, 1, observer, source, FixedDiceProvider([15]), setup)
    assert event.check_dc == 19 and event.check_succeeded
    assert observer.state.action_available
    assert not observer.state.bonus_action_available


def test_missing_ability_sight_active_disguise_or_distinct_owner_fail_closed():
    setup, source, observer = _battle()
    with pytest.raises(ValueError, match="different creature"):
        resolve_visual_disguise_inspection(1, 1, source, source, FixedDiceProvider([20]), setup)
    source.state.magical_visual_disguise_active = False
    with pytest.raises(ValueError, match="active source-declared"):
        resolve_visual_disguise_inspection(1, 1, observer, source, FixedDiceProvider([20]), setup)
    source.state.magical_visual_disguise_active = True
    observer.state.active_effect_ids.append("blinded")
    with pytest.raises(ValueError, match="requires sight"):
        resolve_visual_disguise_inspection(1, 1, observer, source, FixedDiceProvider([20]), setup)
