from app.combat.attack_actions import resolve_attack_action
from app.combat.conditions import apply_condition, has_condition
from app.combat.d20_tests import resolve_ability_check, resolve_saving_throw
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.srd_monsters import build_skeleton
from app.domain.models import Ability, BattlefieldState, ConditionType, RollMode, Skill


def test_poisoned_attacker_has_disadvantage() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    apply_condition(fighter, ConditionType.POISONED, goblin)

    events = resolve_attack_action(
        1, 1, fighter, goblin, BattlefieldState(distance_ft=5), FixedDiceProvider([18, 2])
    )

    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.DISADVANTAGE
    assert events[0].attack_roll.rolls == [18, 2]


def test_poisoned_ability_check_has_disadvantage() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.POISONED)

    roll, success = resolve_ability_check(
        fighter, Skill.ATHLETICS, 10, FixedDiceProvider([18, 4])
    )

    assert roll.mode is RollMode.DISADVANTAGE
    assert roll.rolls == [18, 4]
    assert roll.total == 9
    assert success is False


def test_poisoned_does_not_affect_saving_throws() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.POISONED)

    roll, success = resolve_saving_throw(
        fighter, Ability.STRENGTH, 15, FixedDiceProvider([10])
    )

    assert roll.mode is RollMode.NORMAL
    assert roll.rolls == [10]
    assert roll.total == 15
    assert success is True


def test_skeleton_is_immune_to_poisoned_condition() -> None:
    skeleton = build_combatant_state(build_skeleton())
    fighter = build_combatant_state(build_demo_fighter())

    applied = apply_condition(skeleton, ConditionType.POISONED, fighter)

    assert applied is False
    assert not has_condition(skeleton, ConditionType.POISONED)
