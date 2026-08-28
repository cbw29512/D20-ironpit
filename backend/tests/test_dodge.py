import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.dodge import has_dodge_benefits, take_dodge_action
from app.combat.saving_throws import resolve_saving_throw
from app.combat.state import begin_turn, build_combatant_state, end_turn
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import AbilityKind, ConditionKind, RollMode


class NoRollDiceProvider:
    def roll(self, sides: int) -> int:
        raise AssertionError(f"Automatic failure must not roll d{sides}.")


def test_dodge_spends_action_and_preserves_other_turn_resources() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    event = take_dodge_action(1, 1, fighter)

    assert event.event_type == "dodge"
    assert fighter.action_available is False
    assert fighter.bonus_action_available is True
    assert fighter.reaction_available is True
    assert fighter.dodging is True
    assert has_dodge_benefits(fighter) is True


def test_incapacitated_creature_cannot_take_dodge() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    fighter.conditions.add(ConditionKind.INCAPACITATED)

    with pytest.raises(ValueError, match="Incapacitated"):
        take_dodge_action(1, 1, fighter)


def test_visible_attack_against_dodging_target_has_disadvantage() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    take_dodge_action(1, 1, goblin)

    event = resolve_attack(
        2, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([18, 5]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.DISADVANTAGE
    assert event.attack_roll.rolls == [18, 5]
    assert event.hit is False


def test_dodge_does_not_penalize_an_attacker_the_dodger_cannot_see() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    fighter.conditions.add(ConditionKind.INVISIBLE)
    take_dodge_action(1, 1, goblin)

    event = resolve_attack(
        2, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([5, 18, 4]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 18


def test_dodge_grants_advantage_only_to_dexterity_saves() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    take_dodge_action(1, 1, goblin)

    dexterity = resolve_saving_throw(
        goblin, AbilityKind.DEXTERITY, 15, FixedDiceProvider([5, 14])
    )
    wisdom = resolve_saving_throw(
        goblin, AbilityKind.WISDOM, 10, FixedDiceProvider([11])
    )

    assert dexterity.roll is not None
    assert dexterity.roll.mode is RollMode.ADVANTAGE
    assert dexterity.roll.selected_roll == 14
    assert dexterity.success is True
    assert wisdom.roll is not None
    assert wisdom.roll.mode is RollMode.NORMAL


def test_dodge_dexterity_advantage_cancels_other_disadvantage() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    take_dodge_action(1, 1, goblin)

    result = resolve_saving_throw(
        goblin,
        AbilityKind.DEXTERITY,
        14,
        FixedDiceProvider([12]),
        disadvantage_sources=1,
    )

    assert result.roll is not None
    assert result.roll.mode is RollMode.NORMAL
    assert result.roll.total == 14


def test_dodge_benefits_are_lost_while_incapacitated() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    take_dodge_action(1, 1, goblin)
    goblin.conditions.add(ConditionKind.INCAPACITATED)

    event = resolve_attack(
        2, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([5]),
    )

    assert goblin.dodging is True
    assert has_dodge_benefits(goblin) is False
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL


def test_speed_zero_creature_can_take_dodge_but_gets_no_benefit() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    template = build_goblin_warrior().model_copy(update={"speed_ft": 0})
    goblin = build_combatant_state(template)
    take_dodge_action(1, 1, goblin)

    event = resolve_attack(
        2, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([5]),
    )

    assert goblin.dodging is True
    assert has_dodge_benefits(goblin) is False
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL


def test_paralyzed_overrides_active_dodge_benefits() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    take_dodge_action(1, 1, goblin)
    goblin.conditions.add(ConditionKind.PARALYZED)

    event = resolve_attack(
        2, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([5, 18, 4, 5]),
    )
    dexterity = resolve_saving_throw(
        goblin, AbilityKind.DEXTERITY, 1, NoRollDiceProvider()
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.critical is True
    assert dexterity.automatic_failure is True
    assert dexterity.success is False


def test_dodge_expires_at_start_of_dodgers_next_turn_not_end() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    take_dodge_action(1, 1, fighter)

    end_turn(fighter)
    assert fighter.dodging is True
    assert has_dodge_benefits(fighter) is True

    begin_turn(fighter)
    assert fighter.dodging is False
    assert has_dodge_benefits(fighter) is False
