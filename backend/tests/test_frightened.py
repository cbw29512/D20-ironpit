import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.condition_timing import expire_turn_conditions
from app.combat.conditions import apply_condition, has_condition
from app.combat.d20_tests import resolve_ability_check
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.combat.turns import prepare_attack
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import (
    BattlefieldState,
    ConditionExpiry,
    ConditionType,
    RollMode,
    Skill,
)


def _frightened_fighter():
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    apply_condition(fighter, ConditionType.FRIGHTENED, goblin)
    return fighter, goblin


def test_frightened_requires_a_source() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    with pytest.raises(ValueError, match="fear source"):
        apply_condition(fighter, ConditionType.FRIGHTENED)


def test_frightened_attack_disadvantage_requires_visible_source() -> None:
    fighter, goblin = _frightened_fighter()
    battlefield = BattlefieldState(distance_ft=5)

    visible = resolve_attack_action(
        1, 1, fighter, goblin, battlefield, FixedDiceProvider([18, 5]), {"goblin-1"}
    )
    fighter.action_available = True
    hidden = resolve_attack_action(
        2, 1, fighter, goblin, battlefield, FixedDiceProvider([5]), set()
    )

    assert visible[0].attack_roll.mode is RollMode.DISADVANTAGE
    assert hidden[0].attack_roll.mode is RollMode.NORMAL


def test_frightened_ability_check_disadvantage_requires_visible_source() -> None:
    fighter, goblin = _frightened_fighter()

    visible, _ = resolve_ability_check(
        fighter, Skill.ATHLETICS, 10, FixedDiceProvider([18, 4]), {goblin.instance_id}
    )
    hidden, _ = resolve_ability_check(
        fighter, Skill.ATHLETICS, 10, FixedDiceProvider([4]), set()
    )

    assert visible.mode is RollMode.DISADVANTAGE
    assert hidden.mode is RollMode.NORMAL


def test_frightened_creature_cannot_willingly_approach_source() -> None:
    fighter, goblin = _frightened_fighter()
    battlefield = BattlefieldState(distance_ft=30)
    begin_turn(fighter)

    attack, events, _ = prepare_attack(1, 1, fighter, goblin, battlefield)

    assert attack is None
    assert events == []
    assert battlefield.distance_ft == 30
    assert fighter.movement_remaining_ft == 30
    assert fighter.action_available is True


def test_source_turn_start_expiry_removes_frightened() -> None:
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    goblin = build_combatant_state(build_goblin_warrior(), "goblin-1")
    apply_condition(
        fighter,
        ConditionType.FRIGHTENED,
        goblin,
        expires_on=ConditionExpiry.SOURCE_TURN_START,
    )

    events = expire_turn_conditions(1, 2, goblin, [fighter, goblin], "start")

    assert len(events) == 1
    assert events[0].condition is ConditionType.FRIGHTENED
    assert events[0].condition_active is False
    assert not has_condition(fighter, ConditionType.FRIGHTENED)
