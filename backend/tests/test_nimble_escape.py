from app.combat.attack_actions import resolve_attack_action
from app.combat.bonus_actions import (
    use_nimble_escape_disengage,
    use_nimble_escape_hide,
)
from app.combat.dice import FixedDiceProvider
from app.combat.engine import run_duel
from app.combat.state import begin_turn, build_combatant_state, end_turn
from app.combat.turns import (
    prepare_attack,
    prepare_nimble_hide,
    prepare_skirmish_retreat,
)
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import (
    ActorVisibilityState,
    BattlefieldState,
    ConditionKind,
    CoverLevel,
    RollMode,
)


def hideable_battlefield(actor_id: str, distance_ft: int = 30) -> BattlefieldState:
    return BattlefieldState(
        distance_ft=distance_ft,
        visibility_by_actor={
            actor_id: ActorVisibilityState(
                cover=CoverLevel.THREE_QUARTERS,
                enemy_line_of_sight=False,
            )
        },
    )


def test_goblin_roster_has_nimble_escape_and_srd_stealth_data() -> None:
    goblin = build_goblin_warrior()
    assert goblin.bonus_action_features == ["nimble-escape"]
    assert goblin.skill_bonuses["stealth"] == 6
    assert goblin.passive_perception == 9


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


def test_nimble_escape_hide_spends_bonus_action_but_not_action() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = hideable_battlefield(goblin.template.id)
    begin_turn(goblin)

    event = use_nimble_escape_hide(
        1, 1, goblin, battlefield, FixedDiceProvider([9])
    )

    assert event.event_type == "hide"
    assert event.feature_id == "nimble-escape"
    assert event.check_roll is not None
    assert event.check_roll.total == 15
    assert goblin.bonus_action_available is False
    assert goblin.action_available is True
    assert goblin.hidden is True
    assert ConditionKind.INVISIBLE in goblin.conditions


def test_failed_nimble_escape_hide_still_spends_bonus_action_not_action() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = hideable_battlefield(goblin.template.id)
    begin_turn(goblin)

    event = use_nimble_escape_hide(
        1, 1, goblin, battlefield, FixedDiceProvider([8])
    )

    assert event.check_roll is not None
    assert event.check_roll.total == 14
    assert goblin.bonus_action_available is False
    assert goblin.action_available is True
    assert goblin.hidden is False


def test_nimble_escape_retreat_suppresses_opportunity_attack() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=5)
    begin_turn(goblin)

    events, next_sequence = prepare_skirmish_retreat(
        1, 1, goblin, fighter, battlefield, FixedDiceProvider([20])
    )

    assert [event.event_type for event in events] == ["disengage", "movement"]
    assert events[1].animation == "retreat"
    assert battlefield.distance_ft == 35
    assert goblin.movement_remaining_ft == 0
    assert fighter.reaction_available is True
    assert next_sequence == 3


def test_melee_disengage_priority_prevents_same_turn_nimble_hide() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = hideable_battlefield(goblin.template.id, distance_ft=5)
    begin_turn(goblin)

    retreat_events, sequence = prepare_skirmish_retreat(
        1, 1, goblin, fighter, battlefield, FixedDiceProvider([20])
    )
    hide_events, sequence = prepare_nimble_hide(
        sequence, 1, goblin, battlefield, FixedDiceProvider([20])
    )

    assert [event.event_type for event in retreat_events] == ["disengage", "movement"]
    assert hide_events == []
    assert goblin.bonus_action_available is False
    assert goblin.hidden is False
    assert sequence == 3


def test_open_arena_nimble_hide_is_noop() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(distance_ft=30)
    begin_turn(goblin)

    events, sequence = prepare_nimble_hide(
        4, 1, goblin, battlefield, FixedDiceProvider([20])
    )

    assert events == []
    assert sequence == 4
    assert goblin.bonus_action_available is True


def test_nimble_hide_then_shortbow_attack_has_advantage_and_reveals() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = hideable_battlefield(goblin.template.id)
    begin_turn(goblin)

    hide_events, sequence = prepare_nimble_hide(
        1, 1, goblin, battlefield, FixedDiceProvider([9])
    )
    attack, prep_events, sequence = prepare_attack(
        sequence, 1, goblin, battlefield
    )
    assert attack is not None
    attack_events, sequence = resolve_attack_action(
        sequence,
        1,
        goblin,
        fighter,
        attack,
        battlefield.distance_ft,
        FixedDiceProvider([14, 10, 3, 2]),
    )

    assert [event.event_type for event in hide_events] == ["hide"]
    assert prep_events == []
    assert attack.weapon.id == "shortbow"
    assert attack_events[0].attack_roll is not None
    assert attack_events[0].attack_roll.mode is RollMode.ADVANTAGE
    assert attack_events[0].damage_roll is not None
    assert attack_events[0].damage_roll.total == 7
    assert goblin.hidden is False
    assert ConditionKind.INVISIBLE not in goblin.conditions
    assert goblin.bonus_action_available is False
    assert sequence == 3


def test_full_open_duel_goblin_disengages_retreats_and_fires_shortbow() -> None:
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
