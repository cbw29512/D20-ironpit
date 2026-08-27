import pytest

from app.combat.movement import move_toward_target, take_dash
from app.combat.policy import select_weapon_attack
from app.combat.state import begin_turn, build_combatant_state
from app.combat.turns import prepare_attack
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import BattlefieldState


def test_fighter_moves_up_to_speed_toward_melee_reach() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=90)
    begin_turn(fighter)

    event = move_toward_target(
        1, 1, fighter, goblin.instance_id, battlefield, desired_distance_ft=5
    )

    assert event is not None
    assert event.movement_ft == 30
    assert battlefield.distance_ft == 60
    assert fighter.movement_remaining_ft == 0


def test_dash_spends_action_and_adds_speed_to_movement() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=60)
    begin_turn(fighter)
    fighter.movement_remaining_ft = 0

    event = take_dash(1, 1, fighter, battlefield)

    assert event.event_type == "dash"
    assert fighter.action_available is False
    assert fighter.movement_remaining_ft == 30
    with pytest.raises(ValueError, match="Action is not available"):
        take_dash(2, 1, fighter, battlefield)


def test_prepare_attack_dashes_when_melee_only_target_is_too_far() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=90)
    begin_turn(fighter)

    attack, events, next_sequence = prepare_attack(1, 1, fighter, goblin, battlefield)

    assert attack is None
    assert [event.event_type for event in events] == ["movement", "dash", "movement"]
    assert battlefield.distance_ft == 30
    assert fighter.action_available is False
    assert next_sequence == 4


def test_prepare_attack_can_move_then_attack_without_dashing() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=30)
    begin_turn(fighter)

    attack, events, _ = prepare_attack(1, 2, fighter, goblin, battlefield)

    assert attack is not None
    assert attack.weapon.id == "longsword"
    assert [event.event_type for event in events] == ["movement"]
    assert battlefield.distance_ft == 5
    assert fighter.action_available is True


def test_goblin_advances_before_using_shortbow_at_range() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=90)
    begin_turn(goblin)

    attack, events, _ = prepare_attack(1, 1, goblin, fighter, battlefield)

    assert [event.event_type for event in events] == ["movement"]
    assert battlefield.distance_ft == 60
    assert attack is not None
    assert attack.weapon.id == "shortbow"
    assert goblin.action_available is True


def test_goblin_closes_knockback_gap_and_returns_to_melee() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=15)
    begin_turn(goblin)

    attack, events, _ = prepare_attack(1, 3, goblin, fighter, battlefield)

    assert [event.event_type for event in events] == ["movement"]
    assert events[0].distance_before_ft == 15
    assert events[0].distance_after_ft == 5
    assert attack is not None
    assert attack.weapon.id == "scimitar"


def test_goblin_prefers_melee_when_already_engaged() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    attack = select_weapon_attack(goblin, distance_ft=5)

    assert attack is not None
    assert attack.weapon.id == "scimitar"


def test_goblin_selects_shortbow_when_scimitar_is_out_of_reach() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    attack = select_weapon_attack(goblin, distance_ft=90)

    assert attack is not None
    assert attack.weapon.id == "shortbow"
