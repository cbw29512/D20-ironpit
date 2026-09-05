import pytest

from app.combat.encounter_movement import move_toward_combatant, take_encounter_dash
from app.combat.encounter_targeting import combatant_distance
from app.combat.policy import select_weapon_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant


def _member(combatant_id: str, side: str, position: int, template) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_fighter_moves_up_to_speed_toward_melee_reach() -> None:
    fighter = _member("hero-1", "heroes", 0, build_demo_fighter())
    target = _member("monster-1", "monsters", 90, build_goblin_warrior())
    begin_turn(fighter.state)

    event = move_toward_combatant(1, 1, fighter, target, desired_distance_ft=5)

    assert event is not None and event.movement_ft == 30
    assert combatant_distance(fighter, target) == 60
    assert fighter.state.movement_remaining_ft == 0


def test_dash_spends_action_and_adds_effective_speed_to_movement() -> None:
    fighter = _member("hero-1", "heroes", 0, build_demo_fighter())
    target = _member("monster-1", "monsters", 60, build_goblin_warrior())
    begin_turn(fighter.state)
    fighter.state.movement_remaining_ft = 0

    event = take_encounter_dash(1, 1, fighter, target)

    assert event.event_type == "dash"
    assert fighter.state.action_available is False
    assert fighter.state.movement_remaining_ft == 30
    with pytest.raises(ValueError, match="Action is not available"):
        take_encounter_dash(2, 1, fighter, target)


def test_movement_and_dash_primitives_compose_without_a_second_turn_engine() -> None:
    fighter = _member("hero-1", "heroes", 0, build_demo_fighter())
    target = _member("monster-1", "monsters", 90, build_goblin_warrior())
    begin_turn(fighter.state)

    first = move_toward_combatant(1, 1, fighter, target, 5)
    dash = take_encounter_dash(2, 1, fighter, target)
    second = move_toward_combatant(3, 1, fighter, target, 5)

    assert [first.event_type, dash.event_type, second.event_type] == ["movement", "dash", "movement"]
    assert combatant_distance(fighter, target) == 30
    assert fighter.state.action_available is False


def test_move_to_melee_range_preserves_action_for_attack() -> None:
    fighter = _member("hero-1", "heroes", 0, build_demo_fighter())
    target = _member("monster-1", "monsters", 30, build_goblin_warrior())
    begin_turn(fighter.state)

    event = move_toward_combatant(1, 2, fighter, target, 5)
    attack = select_weapon_attack(fighter.state, combatant_distance(fighter, target))

    assert event is not None and event.movement_ft == 25
    assert attack is not None and attack.weapon.id == "longsword"
    assert fighter.state.action_available is True


def test_goblin_selects_shortbow_when_scimitar_is_out_of_reach() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    attack = select_weapon_attack(goblin, distance_ft=90)

    assert attack is not None
    assert attack.weapon.id == "shortbow"
