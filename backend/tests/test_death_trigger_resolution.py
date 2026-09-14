from __future__ import annotations

from app.combat.death_triggers import resolve_death_triggers, resolve_event_death_triggers
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.grid import GridPosition


def _template(name: str):
    return next(item for item in build_arena_roster().monsters if item.name == name)


def _member(combatant_id: str, template, x: int, side: str) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=0)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _event(target_id: str, *, is_dead: bool) -> BattleEvent:
    return BattleEvent(
        sequence=1, round_number=1, event_type="attack", actor_id="hero", actor_name="Hero",
        target_id=target_id, target_name=target_id, is_dead=is_dead,
        animation="attack", description="test event",
    )


def test_death_burst_uses_one_damage_roll_and_independent_saves() -> None:
    source = _member("magma", _template("Magma Mephit"), 0, "monsters")
    first = _member("first", _template("Goblin Warrior"), 1, "heroes")
    second = _member("second", _template("Goblin Warrior"), 1, "heroes")
    source.state.current_hp = 0
    source.state.is_alive = False
    source.state.is_dead = True
    setup = EncounterSetup(
        heroes=[first, second], monsters=[source], hero_total_levels=1, monster_total_cr="1/2"
    )

    events, sequence = resolve_death_triggers(
        10, 2, source, setup, FixedDiceProvider([1, 6, 6, 20])
    )

    assert sequence == 12
    assert len(events) == 2
    assert events[0].feature_id == "death-burst"
    assert events[0].save_succeeded is False
    assert events[1].save_succeeded is True
    assert events[0].damage_components[0].rolls == [6, 6]
    assert events[1].damage_components[0].rolls == [6, 6]
    assert events[0].damage_components[0].total == 12
    assert events[1].damage_components[0].total == 6


def test_death_burst_is_once_only_for_same_source_effect() -> None:
    source = _member("magma", _template("Magma Mephit"), 0, "monsters")
    target = _member("target", _template("Goblin Warrior"), 1, "heroes")
    source.state.current_hp = 0
    source.state.is_alive = False
    source.state.is_dead = True
    setup = EncounterSetup(
        heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="1/2"
    )
    resolved: set[str] = set()

    first, sequence = resolve_death_triggers(
        1, 1, source, setup, FixedDiceProvider([20, 2, 2]), resolved=resolved
    )
    second, final_sequence = resolve_death_triggers(
        sequence, 1, source, setup, FixedDiceProvider([20]), resolved=resolved
    )

    assert len(first) == 1
    assert second == []
    assert final_sequence == sequence
    assert resolved == {"magma:death-burst"}


def test_event_dispatch_requires_event_to_record_death_and_is_once_only() -> None:
    source = _member("magma", _template("Magma Mephit"), 0, "monsters")
    target = _member("target", _template("Goblin Warrior"), 1, "heroes")
    source.state.current_hp = 0
    source.state.is_alive = False
    source.state.is_dead = True
    setup = EncounterSetup(heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="1/2")
    resolved: set[str] = set()

    skipped, sequence = resolve_event_death_triggers(
        5, 1, _event("magma", is_dead=False), setup, FixedDiceProvider([]), resolved=resolved,
    )
    assert skipped == []
    assert sequence == 5

    fired, sequence = resolve_event_death_triggers(
        sequence, 1, _event("magma", is_dead=True), setup,
        FixedDiceProvider([20, 2, 2]), resolved=resolved,
    )
    repeated, final_sequence = resolve_event_death_triggers(
        sequence, 1, _event("magma", is_dead=True), setup, FixedDiceProvider([]), resolved=resolved,
    )
    assert len(fired) == 1
    assert repeated == []
    assert final_sequence == sequence
