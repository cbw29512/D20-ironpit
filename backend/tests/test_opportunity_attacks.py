from app.combat.conditions import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.disengage import take_disengage
from app.combat.retreat import move_away_from_target
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.srd_beasts import build_giant_crab
from app.domain.models import BattlefieldState, ConditionType


def test_voluntary_movement_out_of_reach_triggers_reaction_before_move() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    events = move_away_from_target(
        1, 1, goblin, fighter, battlefield, 10, FixedDiceProvider([10, 2])
    )

    assert [event.event_type for event in events] == ["attack", "movement"]
    assert events[0].feature_id == "opportunity-attack"
    assert events[0].distance_before_ft is None
    assert events[1].distance_before_ft == 5
    assert events[1].distance_after_ft == 15
    assert fighter.reaction_available is False


def test_disengage_suppresses_opportunity_attack_for_rest_of_turn() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)
    disengage = take_disengage(1, 1, goblin, battlefield)

    events = move_away_from_target(
        2, 1, goblin, fighter, battlefield, 10, FixedDiceProvider([1])
    )

    assert disengage.feature_id == "disengage"
    assert [event.event_type for event in events] == ["movement"]
    assert fighter.reaction_available is True
    assert battlefield.distance_ft == 15


def test_unseen_mover_does_not_provoke_opportunity_attack() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    events = move_away_from_target(
        1,
        1,
        goblin,
        fighter,
        battlefield,
        10,
        FixedDiceProvider([1]),
        reactor_can_see_mover=False,
    )

    assert [event.event_type for event in events] == ["movement"]
    assert fighter.reaction_available is True


def test_giant_crab_opportunity_claw_can_grapple_and_stop_retreat() -> None:
    crab = build_combatant_state(build_giant_crab(), "crab-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(fighter)

    events = move_away_from_target(
        1, 1, fighter, crab, battlefield, 10, FixedDiceProvider([15, 3])
    )

    assert [event.event_type for event in events] == ["attack", "condition"]
    assert events[0].feature_id == "opportunity-attack"
    assert has_condition(fighter, ConditionType.GRAPPLED)
    assert fighter.movement_remaining_ft == 0
    assert battlefield.distance_ft == 5
    assert crab.reaction_available is False


def test_disengage_state_resets_at_start_of_next_turn() -> None:
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)
    take_disengage(1, 1, goblin, battlefield)
    assert goblin.disengaged_this_turn is True

    begin_turn(goblin)

    assert goblin.disengaged_this_turn is False
    assert goblin.action_available is True
