"""Source-neutral subsequent-turn source maintenance lifecycle regressions."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.combat.source_maintenance import (
    resolve_source_maintenance,
    stop_source_maintained_effects,
)
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_effects import TimedEffect


def _member(combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position_ft,
        state=build_combatant_state(build_demo_fighter()),
    )


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterCombatant, EncounterSetup]:
    source = _member("renamed-source", "monsters", 0)
    first = _member("first-target", "heroes", 5)
    second = _member("second-target", "heroes", 10)
    setup = EncounterSetup(
        heroes=[first, second], monsters=[source], ruleset="2014",
        hero_total_levels=2, monster_total_cr="1",
    )
    return source, first, second, setup


def _apply(target: EncounterCombatant, source: EncounterCombatant, effect_id: str) -> None:
    apply_timed_condition(
        target.state, "charmed", source.combatant_id,
        source_effect_id=effect_id,
        source_maintenance_action_cost="bonus_action",
        source_turn_count_at_application=source.state.turns_started,
        source_effect_immunity_on_end=True,
        use_default_poison_recovery=False,
    )


def test_maintenance_is_due_on_next_source_turn_not_same_turn() -> None:
    source, first, second, setup = _setup()
    _apply(first, source, "renamed-song")
    _apply(second, source, "renamed-song")

    events, sequence = resolve_source_maintenance(1, 1, source, setup)
    assert (events, sequence) == ([], 1)
    assert source.state.bonus_action_available is True

    source.state.turns_started = 1
    events, sequence = resolve_source_maintenance(1, 1, source, setup)

    assert sequence == 2
    assert [event.feature_id for event in events] == ["renamed-song"]
    assert source.state.bonus_action_available is False
    assert all(
        target.state.timed_effects[0].source_turn_count_at_application == 1
        for target in (first, second)
    )


def test_unavailable_maintenance_ends_group_without_success_immunity() -> None:
    source, first, second, setup = _setup()
    _apply(first, source, "renamed-song")
    _apply(second, source, "renamed-song")
    source.state.turns_started = 1
    source.state.bonus_action_available = False

    events, sequence = resolve_source_maintenance(4, 2, source, setup)

    assert sequence == 6
    assert len(events) == 2
    assert not first.state.timed_effects
    assert not second.state.timed_effects
    assert "charmed" not in first.state.active_effect_ids
    assert not any("success-immunity" in effect.effect_id for effect in first.state.timed_effects)


def test_voluntary_stop_is_immediate_and_free() -> None:
    source, first, _second, setup = _setup()
    _apply(first, source, "renamed-song")

    events, sequence = stop_source_maintained_effects(7, 1, source, setup)

    assert sequence == 8
    assert events[0].removed_condition_ids == ["charmed"]
    assert source.state.bonus_action_available is True
    assert not first.state.timed_effects


def test_only_best_supported_group_is_continued() -> None:
    source, first, second, setup = _setup()
    _apply(first, source, "wide-control")
    _apply(second, source, "wide-control")
    _apply(first, source, "narrow-control")
    source.state.turns_started = 1

    events, _sequence = resolve_source_maintenance(1, 2, source, setup)

    assert events[0].feature_id == "wide-control"
    assert any(event.feature_id == "narrow-control" for event in events[1:])
    assert all(
        any(effect.source_effect_id == "wide-control" for effect in target.state.timed_effects)
        for target in (first, second)
    )
    assert not any(
        effect.source_effect_id == "narrow-control" for effect in first.state.timed_effects
    )


def test_runtime_maintenance_requires_application_turn_snapshot() -> None:
    with pytest.raises(ValidationError, match="source turn count"):
        TimedEffect(
            effect_id="charmed", source_id="source",
            source_effect_id="renamed-song",
            source_maintenance_action_cost="bonus_action",
        )
