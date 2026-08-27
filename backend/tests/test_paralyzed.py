from app.combat.attacks import resolve_attack
from app.combat.conditions import apply_condition
from app.combat.d20_tests import resolve_saving_throw
from app.combat.dice import FixedDiceProvider
from app.combat.initiative import roll_initiative_order
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import Ability, ConditionType, RollMode


def test_paralyzed_turn_has_no_actions_reaction_or_speed() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PARALYZED)

    begin_turn(fighter)

    assert fighter.action_available is False
    assert fighter.bonus_action_available is False
    assert fighter.reaction_available is False
    assert fighter.movement_remaining_ft == 0


def test_paralyzed_auto_fails_strength_and_dexterity_saves_without_roll() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PARALYZED)
    dice = FixedDiceProvider([14])

    strength_roll, strength_success = resolve_saving_throw(
        fighter, Ability.STRENGTH, 1, dice
    )
    wisdom_roll, wisdom_success = resolve_saving_throw(
        fighter, Ability.WISDOM, 10, dice
    )

    assert strength_roll is None
    assert strength_success is False
    assert wisdom_roll is not None
    assert wisdom_roll.selected_roll == 14
    assert wisdom_success is True


def test_melee_hit_against_paralyzed_target_is_critical() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    apply_condition(goblin, ConditionType.PARALYZED, fighter)

    event = resolve_attack(
        1,
        1,
        fighter,
        goblin,
        fighter.template.weapon_attack,
        5,
        FixedDiceProvider([5, 15, 2, 3]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.hit is True
    assert event.critical is True
    assert event.damage_components[0].notation == "2d8+3"


def test_ranged_hit_beyond_five_feet_is_not_auto_critical() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    apply_condition(fighter, ConditionType.PARALYZED, goblin)
    shortbow = goblin.template.alternate_weapon_attacks[0]

    event = resolve_attack(
        1, 1, goblin, fighter, shortbow, 10, FixedDiceProvider([6, 14, 3])
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.hit is True
    assert event.critical is False


def test_paralyzed_creature_rolls_initiative_with_disadvantage() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())
    apply_condition(fighter, ConditionType.PARALYZED)

    events, order, _ = roll_initiative_order(
        1, [fighter, goblin], FixedDiceProvider([18, 4, 10])
    )

    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.DISADVANTAGE
    assert fighter.initiative_total == 5
    assert order[0] is goblin
