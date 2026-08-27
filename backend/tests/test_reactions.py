from app.combat.dice import FixedDiceProvider
from app.combat.general_actions import take_disengage
from app.combat.movement import move_away_from_target
from app.combat.reactions import resolve_opportunity_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import BattlefieldState


def _states():
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    return fighter, goblin


def test_leaving_visible_reach_triggers_one_weapon_opportunity_attack() -> None:
    fighter, goblin = _states()

    event = resolve_opportunity_attack(
        1, 1, fighter, goblin, 5, 10, FixedDiceProvider([10, 5])
    )

    assert event is not None
    assert event.event_type == "opportunity_attack"
    assert event.weapon_id == "longsword"
    assert event.hit is True
    assert fighter.reaction_available is False

    second = resolve_opportunity_attack(
        2, 1, fighter, goblin, 5, 10, FixedDiceProvider([20, 8, 8])
    )
    assert second is None


def test_ranged_only_profile_falls_back_to_unarmed_opportunity_attack() -> None:
    fighter_template = build_demo_fighter()
    shortbow = build_goblin_warrior().alternate_weapon_attacks[0]
    fighter_template = fighter_template.model_copy(update={
        "weapon_attack": shortbow,
        "alternate_weapon_attacks": [],
    })
    fighter = build_combatant_state(fighter_template, "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")

    event = resolve_opportunity_attack(
        1, 1, fighter, goblin, 5, 10, FixedDiceProvider([10])
    )

    assert event is not None
    assert event.event_type == "opportunity_attack"
    assert event.feature_id == "unarmed-strike"
    assert event.weapon_id is None
    assert event.damage_applied == 4
    assert fighter.reaction_available is False


def test_disengage_consumes_action_and_suppresses_opportunity_attack() -> None:
    fighter, goblin = _states()
    event = take_disengage(1, 1, goblin)

    assert event.event_type == "disengage"
    assert goblin.action_available is False
    assert goblin.disengaged_this_turn is True
    assert resolve_opportunity_attack(
        2, 1, fighter, goblin, 5, 10, FixedDiceProvider([20, 8, 8])
    ) is None
    assert fighter.reaction_available is True


def test_forced_movement_and_teleport_do_not_provoke() -> None:
    fighter, goblin = _states()

    forced = resolve_opportunity_attack(
        1,
        1,
        fighter,
        goblin,
        5,
        15,
        FixedDiceProvider([20, 8, 8]),
        movement_uses_mover_economy=False,
    )
    teleported = resolve_opportunity_attack(
        2,
        1,
        fighter,
        goblin,
        5,
        30,
        FixedDiceProvider([20, 8, 8]),
        teleport=True,
    )

    assert forced is None
    assert teleported is None
    assert fighter.reaction_available is True


def test_staying_in_reach_or_being_unseen_does_not_provoke() -> None:
    fighter, goblin = _states()

    assert resolve_opportunity_attack(
        1, 1, fighter, goblin, 5, 5, FixedDiceProvider([20, 8, 8])
    ) is None
    assert resolve_opportunity_attack(
        2,
        1,
        fighter,
        goblin,
        5,
        10,
        FixedDiceProvider([20, 8, 8]),
        mover_visible=False,
    ) is None
    assert fighter.reaction_available is True


def test_voluntary_departure_resolves_reaction_before_movement() -> None:
    fighter, goblin = _states()
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    events = move_away_from_target(
        1, 1, goblin, fighter, battlefield, 5, FixedDiceProvider([10, 5])
    )

    assert [event.event_type for event in events] == ["opportunity_attack", "movement"]
    assert events[0].distance_before_ft is None
    assert events[1].distance_before_ft == 5
    assert events[1].distance_after_ft == 10
    assert battlefield.distance_ft == 10
    assert fighter.reaction_available is False


def test_lethal_opportunity_attack_stops_departure_before_it_happens() -> None:
    fighter, goblin = _states()
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    events = move_away_from_target(
        1, 1, goblin, fighter, battlefield, 5, FixedDiceProvider([20, 8, 8])
    )

    assert [event.event_type for event in events] == ["opportunity_attack"]
    assert goblin.is_alive is False
    assert battlefield.distance_ft == 5
    assert goblin.movement_spent_ft == 0


def test_disengaged_departure_moves_without_reaction() -> None:
    fighter, goblin = _states()
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)
    take_disengage(1, 1, goblin)

    events = move_away_from_target(
        2, 1, goblin, fighter, battlefield, 5, FixedDiceProvider([20, 8, 8])
    )

    assert [event.event_type for event in events] == ["movement"]
    assert battlefield.distance_ft == 10
    assert fighter.reaction_available is True


def test_begin_turn_restores_reaction_and_clears_disengage() -> None:
    fighter, goblin = _states()
    fighter.reaction_available = False
    take_disengage(1, 1, goblin)

    begin_turn(fighter)
    begin_turn(goblin)

    assert fighter.reaction_available is True
    assert goblin.action_available is True
    assert goblin.disengaged_this_turn is False
