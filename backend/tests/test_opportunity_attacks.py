from app.combat.dice import FixedDiceProvider
from app.combat.reactions import retreat_with_opportunity_check
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import BattlefieldState


def test_leaving_reach_triggers_opportunity_attack_before_movement() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(fighter)
    begin_turn(goblin)

    events, next_sequence = retreat_with_opportunity_check(
        1,
        1,
        goblin,
        fighter,
        battlefield,
        FixedDiceProvider([14, 4]),
    )

    assert [event.event_type for event in events] == ["attack", "movement"]
    assert events[0].reaction_id == "opportunity-attack"
    assert events[0].actor_id == fighter.template.id
    assert events[0].target_id == goblin.template.id
    assert events[0].hit is True
    assert events[1].distance_before_ft == 5
    assert events[1].distance_after_ft == 35
    assert fighter.reaction_available is False
    assert fighter.action_available is True
    assert next_sequence == 3


def test_disengage_prevents_opportunity_attack() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(fighter)
    begin_turn(goblin)
    goblin.disengaged = True

    events, next_sequence = retreat_with_opportunity_check(
        1,
        1,
        goblin,
        fighter,
        battlefield,
        FixedDiceProvider([20]),
    )

    assert [event.event_type for event in events] == ["movement"]
    assert battlefield.distance_ft == 35
    assert fighter.reaction_available is True
    assert next_sequence == 2


def test_opportunity_attack_can_defeat_mover_before_it_leaves_reach() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(fighter)
    begin_turn(goblin)

    events, next_sequence = retreat_with_opportunity_check(
        1,
        1,
        goblin,
        fighter,
        battlefield,
        FixedDiceProvider([20, 5, 5]),
    )

    assert len(events) == 1
    assert events[0].reaction_id == "opportunity-attack"
    assert events[0].critical is True
    assert goblin.is_alive is False
    assert battlefield.distance_ft == 5
    assert next_sequence == 2


def test_reaction_refreshes_at_start_of_reactors_next_turn() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    fighter.reaction_available = False

    begin_turn(fighter)

    assert fighter.reaction_available is True
