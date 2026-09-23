from __future__ import annotations

import pytest

from app.combat.initiative_resource_refill import resolve_initiative_resource_refills
from app.combat.state import build_combatant_state
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.models import ResourceDefinition


def _member(
    current: int,
    *,
    maximum: int = 5,
    resource_id: str = "focus",
    grant_resource_id: str = "focus",
) -> EncounterCombatant:
    template = build_karnok_stoneward_2014(1).model_copy(update={
        "id": "initiative-refill-fixture",
        "resources": [ResourceDefinition(id=resource_id, name="Focus", max_uses=maximum)],
        "initiative_resource_refill_grants": [InitiativeResourceRefillGrant(
            source_id="second-breath",
            source_name="Second Breath",
            resource_id=grant_resource_id,
            when_at_or_below=0,
            restore_amount=4,
        )],
    })
    state = build_combatant_state(template)
    if state.resources:
        state.resources[0].current_uses = current
    return EncounterCombatant(
        combatant_id="hero-refill",
        side="heroes",
        position_ft=0,
        state=state,
    )


def _setup(member: EncounterCombatant) -> EncounterSetup:
    target_template = build_karnok_stoneward_2014(1).model_copy(update={
        "id": "initiative-refill-target",
        "initiative_resource_refill_grants": [],
    })
    target = EncounterCombatant(
        combatant_id="monster-target",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(target_template),
    )
    return EncounterSetup(
        heroes=[member],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2014",
    )


def test_initiative_refill_restores_declared_amount_and_logs_source() -> None:
    member = _member(0)
    events, sequence = resolve_initiative_resource_refills(7, _setup(member))

    assert sequence == 8
    assert member.state.resources[0].current_uses == 4
    assert events[0].feature_id == "second-breath"
    assert events[0].resource_remaining == 4
    assert "Second Breath" in events[0].description


def test_initiative_refill_does_not_trigger_above_threshold() -> None:
    member = _member(1)
    events, sequence = resolve_initiative_resource_refills(7, _setup(member))

    assert events == []
    assert sequence == 7
    assert member.state.resources[0].current_uses == 1


def test_initiative_refill_never_exceeds_resource_maximum() -> None:
    member = _member(0, maximum=3)
    events, _ = resolve_initiative_resource_refills(1, _setup(member))

    assert member.state.resources[0].current_uses == 3
    assert events[0].resource_remaining == 3


def test_initiative_refill_fails_closed_for_missing_resource() -> None:
    member = _member(0, grant_resource_id="missing")
    with pytest.raises(ValueError, match="references missing resource missing"):
        resolve_initiative_resource_refills(1, _setup(member))
