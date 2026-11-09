"""Universal successful shared-square save logs a push without arena movement."""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.combat.saving_throw_effects import SaveEffectResult
from app.combat.saving_throw_event import build_save_event
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.demo import build_demo_fighter
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant
from scripts.browser_template_serializer import _save
from app.content.capability_from_template import _save as reverse_save


def _source():
    return SaveCapabilityDefinition(
        id="homebrew-ebb", name="Ebb Wave", save_ability="strength",
        dc=17, range_ft=0, max_targets=4, target_scope="all-other-creatures",
        area={"shape": "shared-space", "origin": "self"},
        successful_save_exits_source_space=True,
    )


def _member(label: str, side: str):
    template = build_demo_fighter().model_copy(update={"name": label})
    return EncounterCombatant(
        combatant_id=label, side=side, position_ft=0,
        state=build_combatant_state(template),
    )


def _event(saved: bool):
    action = _compile_save(_source())
    owner, target = _member("Source", "monsters"), _member("Victim", "heroes")
    before = (owner.position_ft, target.position_ft)
    event = build_save_event(
        1, 2, owner, target, action,
        SimpleNamespace(
            succeeded=saved, automatic_failure=False, save_roll=None,
            advantage_sources=(), selected_ability="strength",
        ),
        SimpleNamespace(
            damage_outcome=None, damage_roll=None, damage_components=[],
        ),
        SaveEffectResult(applied_conditions=[], pushed_ft=0),
        resource_remaining=None, hp_before=target.state.current_hp,
        temporary_hp_before=0, death_success_before=0,
        death_failure_before=0, concentration_before=None,
    )
    assert before == (owner.position_ft, target.position_ft)
    return event


def test_success_logging_and_legacy_non_success():
    card = _source()
    compiled = _compile_save(card)
    assert compiled.successful_save_exits_source_space
    assert _save(compiled)["successfulSaveExitsSourceSpace"] is True
    assert reverse_save(compiled)["successful_save_exits_source_space"] is True
    assert "pushed out of Source's space" in _event(True).description
    assert "position unchanged by arena rule" in _event(True).description
    assert "pushed out" not in _event(False).description
    default = card.model_copy(update={"successful_save_exits_source_space": False})
    assert "successfulSaveExitsSourceSpace" not in _save(_compile_save(default))


def test_success_exit_requires_actual_shared_source_space():
    with pytest.raises(ValidationError):
        SaveCapabilityDefinition(
            id="bad", name="Bad", save_ability="strength", dc=12,
            range_ft=5, successful_save_exits_source_space=True,
        )
    with pytest.raises(ValidationError):
        SaveCapabilityDefinition(
            id="bad", name="Bad", save_ability="strength", dc=12,
            range_ft=5, area={"shape": "radius", "origin": "self", "radius_ft": 5},
            successful_save_exits_source_space=True,
        )


def test_direct_runtime_template_cannot_skip_source_geometry_validation():
    # Runtime constructors are also used by characters and homebrew, not
    # only the source-adapter compiler. They must share the same fail-closed gate.
    invalid = {
        "id": "generic-undertow", "name": "Undertow",
        "save_ability": "strength", "dc": 11, "range_ft": 5,
        "successful_save_exits_source_space": True,
    }
    with pytest.raises(ValidationError, match="shared-space area"):
        SavingThrowAction(**invalid)
    with pytest.raises(ValidationError, match="shared-space area"):
        SavingThrowAction(**{
            **invalid, "area": {"shape": "radius", "origin": "self", "radius_ft": 5}
        })
    valid = SavingThrowAction(**{
        **invalid, "range_ft": 0,
        "area": {"shape": "shared-space", "origin": "self"},
    })
    assert valid.successful_save_exits_source_space is True
