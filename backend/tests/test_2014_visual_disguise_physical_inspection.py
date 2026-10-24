"""Universal tactile inspection of source-declared visual disguises."""
from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.visual_disguise_physical_inspection import (
    recognize_visual_disguise_by_physical_inspection,
)
from app.domain.models import HitControlEffect, SavingThrowAction
from test_2014_visual_disguise_inspection import _battle


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
        FixedDiceProvider([15, 1]), actor_event_id=observer.combatant_id,
        target_event_id=source.combatant_id, reaction_setup=setup,
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
        FixedDiceProvider([15, 1]), actor_event_id=observer.combatant_id,
        target_event_id=source.combatant_id, reaction_setup=setup,
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
        FixedDiceProvider([15, 1]), actor_event_id=source.combatant_id,
        target_event_id=observer.combatant_id, reaction_setup=setup,
    )

    assert event.hit is True
    assert "grappled" in event.applied_condition_ids
    assert observer.state.recognized_visual_disguise_source_ids == ["source"]
    assert source.state.magical_visual_disguise_active is True


def test_failed_save_grapple_uses_same_tactile_recognition_primitive():
    setup, source, observer = _battle()
    action = SavingThrowAction(
        id="renamed-direct-grab", name="Renamed Direct Grab",
        save_ability="strength", dc=40, range_ft=5, grapple_escape_dc=10,
    )

    event = resolve_save_action(
        1, 1, observer, source, action, 5, FixedDiceProvider([1]), setup=setup,
    )

    assert event.save_succeeded is False
    assert "grappled" in event.applied_condition_ids
    assert observer.state.recognized_visual_disguise_source_ids == ["source"]
    assert "recognizes" in event.description
    assert source.state.magical_visual_disguise_active is True
