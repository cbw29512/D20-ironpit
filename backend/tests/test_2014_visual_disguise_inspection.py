"""Universal card-owned Investigation checks against visual disguises."""
from __future__ import annotations

import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.state import build_combatant_state
from app.combat.visual_disguise import (
    recognize_visual_disguise_by_physical_inspection,
    resolve_visual_disguise_inspection,
)
from app.domain.models import HitControlEffect
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


def test_tactile_inspection_uses_existing_observer_recognition_without_action_cost():
    setup, source, observer = _battle()
    observer.state.active_effect_ids.append("blinded")
    original_action = observer.state.action_available

    recognized = recognize_visual_disguise_by_physical_inspection(
        observer.state, source.state, source.combatant_id,
    )

    assert recognized is True
    assert observer.state.recognized_visual_disguise_source_ids == ["source"]
    assert observer.state.action_available is original_action
    assert source.state.magical_visual_disguise_active is True
    assert source.state.true_form_visible is True
    assert recognize_visual_disguise_by_physical_inspection(
        observer.state, source.state, source.combatant_id,
    ) is False


def test_physical_inspection_flag_false_does_not_invent_recognition():
    _setup_value, source, observer = _battle()
    declared = source.state.template.visual_disguise_action
    source.state.template = source.state.template.model_copy(update={
        "visual_disguise_action": declared.model_copy(update={
            "name": "Renamed Smooth Mask",
            "physical_inspection_inconsistent": False,
        }),
    })

    assert recognize_visual_disguise_by_physical_inspection(
        observer.state, source.state, source.combatant_id,
    ) is False
    assert observer.state.recognized_visual_disguise_source_ids == []
    assert source.state.magical_visual_disguise_active is True


def test_grapple_contact_recognizes_disguise_but_plain_weapon_hit_does_not():
    setup, source, observer = _battle()
    ordinary = observer.state.template.weapon_attack
    assert ordinary is not None

    plain = resolve_attack(
        1, 1, observer.state, source.state, ordinary, 5,
        FixedDiceProvider([15, 1]),
        actor_event_id=observer.combatant_id,
        target_event_id=source.combatant_id,
        reaction_setup=setup,
    )
    assert plain.hit is True
    assert observer.state.recognized_visual_disguise_source_ids == []
    assert source.state.magical_visual_disguise_active is True

    setup, source, observer = _battle()
    grapple_attack = observer.state.template.weapon_attack.model_copy(update={
        "control_effect": HitControlEffect(grapple_escape_dc=10),
    })
    grapple = resolve_attack(
        1, 1, observer.state, source.state, grapple_attack, 5,
        FixedDiceProvider([15, 1]),
        actor_event_id=observer.combatant_id,
        target_event_id=source.combatant_id,
        reaction_setup=setup,
    )
    assert grapple.hit is True
    assert "grappled" in grapple.applied_condition_ids
    assert observer.state.recognized_visual_disguise_source_ids == ["source"]
    assert "recognizes" in grapple.description
    assert source.state.magical_visual_disguise_active is True


def test_disguised_grappler_is_recognized_by_the_creature_it_holds():
    setup, source, observer = _battle()
    grapple_attack = source.state.template.weapon_attack.model_copy(update={
        "control_effect": HitControlEffect(grapple_escape_dc=10),
    })

    event = resolve_attack(
        1, 1, source.state, observer.state, grapple_attack, 5,
        FixedDiceProvider([15, 1]),
        actor_event_id=source.combatant_id,
        target_event_id=observer.combatant_id,
        reaction_setup=setup,
    )

    assert event.hit is True
    assert "grappled" in event.applied_condition_ids
    assert observer.state.recognized_visual_disguise_source_ids == ["source"]
    assert source.state.magical_visual_disguise_active is True
