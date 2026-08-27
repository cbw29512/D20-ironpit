import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.conditions import apply_condition, has_condition, stand_from_prone
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.srd_beasts import build_wolf
from app.domain.models import BattlefieldState, ConditionType, RollMode


def test_wolf_bite_applies_prone_to_medium_target() -> None:
    wolf = build_combatant_state(build_wolf())
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=5)

    events = resolve_attack_action(
        1, 1, wolf, fighter, battlefield, FixedDiceProvider([15, 3])
    )

    assert [event.event_type for event in events] == ["attack", "condition"]
    assert events[1].condition is ConditionType.PRONE
    assert events[1].condition_active is True
    assert has_condition(fighter, ConditionType.PRONE)


def test_prone_attacker_has_disadvantage() -> None:
    wolf = build_combatant_state(build_wolf())
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(wolf, ConditionType.PRONE, fighter)

    events = resolve_attack_action(
        1, 1, wolf, fighter, BattlefieldState(distance_ft=5), FixedDiceProvider([18, 5])
    )

    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.DISADVANTAGE
    assert events[0].attack_roll.rolls == [18, 5]


def test_melee_attack_against_prone_target_has_advantage() -> None:
    wolf = build_combatant_state(build_wolf())
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PRONE, wolf)

    events = resolve_attack_action(
        1, 1, wolf, fighter, BattlefieldState(distance_ft=5), FixedDiceProvider([4, 17, 2])
    )

    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.ADVANTAGE
    assert events[0].attack_roll.selected_roll == 17


def test_ranged_attack_against_distant_prone_target_has_disadvantage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PRONE, goblin)

    events = resolve_attack_action(
        1, 1, goblin, fighter, BattlefieldState(distance_ft=10), FixedDiceProvider([18, 7])
    )

    assert events[0].weapon_id == "shortbow"
    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.DISADVANTAGE


def test_standing_from_prone_costs_half_speed() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PRONE)
    begin_turn(fighter)

    event = stand_from_prone(1, 1, fighter)

    assert event is not None
    assert event.movement_ft == 15
    assert fighter.movement_remaining_ft == 15
    assert not has_condition(fighter, ConditionType.PRONE)


def test_unimplemented_condition_fails_closed() -> None:
    fighter = build_combatant_state(build_demo_fighter())

    with pytest.raises(ValueError, match="not fully implemented"):
        apply_condition(fighter, ConditionType.GRAPPLED)
