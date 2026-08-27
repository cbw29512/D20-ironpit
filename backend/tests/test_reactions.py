from app.combat.dice import FixedDiceProvider
from app.combat.general_actions import take_disengage
from app.combat.reactions import resolve_opportunity_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior


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


def test_begin_turn_restores_reaction_and_clears_disengage() -> None:
    fighter, goblin = _states()
    fighter.reaction_available = False
    take_disengage(1, 1, goblin)

    begin_turn(fighter)
    begin_turn(goblin)

    assert fighter.reaction_available is True
    assert goblin.action_available is True
    assert goblin.disengaged_this_turn is False
