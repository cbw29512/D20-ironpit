from __future__ import annotations

import pytest

from app.combat.resource_conversion import conversion_available, resolve_resource_conversion
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant
from app.domain.resource_conversion import ResourceConversionAction
from app.domain.runtime import CombatantState, ResourceState


def _state():
    template = build_nyra_emberveil_2014(2)
    return CombatantState(
        template=template,
        current_hp=template.max_hp,
        movement_remaining_ft=template.speed_ft,
        resources=[
            ResourceState(id=item.id, name=item.name, current_uses=item.max_uses, max_uses=item.max_uses)
            for item in template.resources
        ],
    )


def _resource(state: CombatantState, resource_id: str) -> ResourceState:
    return next(item for item in state.resources if item.id == resource_id)


def test_resource_conversion_spends_bonus_action_and_allows_temporary_slot_overflow() -> None:
    state = _state()
    slot = _resource(state, "spell-slot-1")
    slot.current_uses = 0
    action = next(
        item for item in state.template.resource_conversion_actions
        if item.id == "create-spell-slot-1"
    )

    assert conversion_available(state, action) is True
    event = resolve_resource_conversion(
        state, action, sequence=1, round_number=1, actor_id="nyra"
    )

    assert state.bonus_action_available is False
    assert _resource(state, "sorcery-points").current_uses == 0
    assert slot.current_uses == 1
    assert event.feature_id == "create-spell-slot-1"


def test_resource_conversion_to_bounded_target_never_exceeds_target_maximum() -> None:
    state = _state()
    points = _resource(state, "sorcery-points")
    points.current_uses = 1
    action = next(
        item for item in state.template.resource_conversion_actions
        if item.id == "convert-spell-slot-1"
    )

    resolve_resource_conversion(
        state, action, sequence=1, round_number=1, actor_id="nyra"
    )

    assert points.current_uses == points.max_uses
    assert _resource(state, "spell-slot-1").current_uses == 2


def test_resource_conversion_fails_closed_when_source_is_unavailable() -> None:
    state = _state()
    points = _resource(state, "sorcery-points")
    points.current_uses = 0
    action = next(
        item for item in state.template.resource_conversion_actions
        if item.id == "create-spell-slot-1"
    )

    assert conversion_available(state, action) is False
    with pytest.raises(ValueError, match="unavailable"):
        resolve_resource_conversion(
            state, action, sequence=1, round_number=1, actor_id="nyra"
        )


def test_resource_conversion_schema_rejects_same_source_and_target() -> None:
    with pytest.raises(ValueError, match="different resources"):
        ResourceConversionAction(
            id="bad",
            name="Bad",
            action_cost="bonus_action",
            source_resource_id="x",
            source_cost=1,
            target_resource_id="x",
            target_gain=1,
        )
