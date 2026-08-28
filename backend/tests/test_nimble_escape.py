from app.combat.bonus_actions import use_nimble_escape_disengage
from app.combat.dice import FixedDiceProvider
from app.combat.engine import run_duel
from app.combat.state import begin_turn, build_combatant_state, end_turn
from app.combat.turns import prepare_skirmish_retreat
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import BattlefieldState, RollMode


def test_goblin_roster_has_nimble_escape() -> None:
    goblin = build_goblin_warrior()
    assert goblin.bonus_action_features == ["nimble-escape"]


def test_nimble_escape_takes_disengage_as_bonus_action() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    event = use_nimble_escape_disengage(1, 1, goblin, battlefield)

    assert event.event_type == "disengage"
    assert event.feature_id == "nimble-escape"
    assert goblin.bonus_action_available is False
    assert goblin.disengaged is True
    end_turn(goblin)
    assert goblin.disengaged is False


def test_nimble_escape_retreat_suppresses_opportunity_attack() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    events, next_sequence = prepare_skirmish_retreat(
        1,
        1,
        goblin,
        fighter,
        battlefield,
        FixedDiceProvider([20]),
    )

    assert [event.event_type for event in events] == ["disengage", "movement"]
    assert events[1].animation == "retreat"
    assert battlefield.distance_ft == 35
    assert goblin.movement_remaining_ft == 0
    assert fighter.reaction_available is True
    assert next_sequence == 3


def test_full_duel_goblin_disengages_retreats_and_fires_shortbow() -> None:
    battle = run_duel(
        build_demo_fighter(),
        build_goblin_warrior(),
        FixedDiceProvider([5, 18, 14, 3, 14, 3, 18, 7, 14, 2]),
    )
    first_round = [event for event in battle.events if event.round_number == 1]
    first_goblin_attack = next(
        event for event in first_round
        if event.event_type == "attack" and event.actor_id == "srd-goblin-warrior"
    )

    assert [event.event_type for event in first_round[:3]] == [
        "disengage", "movement", "attack"
    ]
    assert first_round[1].distance_before_ft == 5
    assert first_round[1].distance_after_ft == 35
    assert first_goblin_attack.weapon_id == "shortbow"
    assert first_goblin_attack.attack_roll is not None
    assert first_goblin_attack.attack_roll.mode is RollMode.NORMAL
    assert battle.winner_id == "aldric-vane-l1"
