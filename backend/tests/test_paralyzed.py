from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.initiative import roll_initiative_order
from app.combat.movement import move_away_from_target, move_toward_target
from app.combat.reactions import resolve_opportunity_attack
from app.combat.saving_throws import resolve_saving_throw
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.rogue import build_demo_rogue
from app.domain.models import (
    AbilityKind,
    ActorVisibilityState,
    BattlefieldState,
    ConditionKind,
    CoverLevel,
    RollMode,
)


class NoRollDiceProvider:
    def roll(self, sides: int) -> int:
        raise AssertionError(f"Automatic failure must not roll d{sides}.")


def paralyze(state):
    state.conditions.add(ConditionKind.PARALYZED)
    return state


def test_paralyzed_inherits_incapacitated_initiative_disadvantage() -> None:
    fighter = paralyze(build_combatant_state(build_demo_fighter()))
    events, _, _ = roll_initiative_order([fighter], FixedDiceProvider([18, 5]))
    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.DISADVANTAGE
    assert events[0].attack_roll.selected_roll == 5


def test_paralyzed_speed_is_zero_at_turn_start_and_mid_turn() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(distance_ft=20)
    begin_turn(fighter)
    assert fighter.movement_remaining_ft == 30
    paralyze(fighter)
    assert move_toward_target(1, 1, fighter, battlefield, 5) is None
    assert move_away_from_target(2, 1, fighter, battlefield) is None
    begin_turn(fighter)
    assert fighter.movement_remaining_ft == 0


def test_paralyzed_auto_fails_strength_and_dexterity_without_rolling() -> None:
    fighter = paralyze(build_combatant_state(build_demo_fighter()))
    battlefield = BattlefieldState(
        visibility_by_actor={
            fighter.template.id: ActorVisibilityState(cover=CoverLevel.THREE_QUARTERS)
        }
    )
    strength = resolve_saving_throw(
        fighter, AbilityKind.STRENGTH, 1, NoRollDiceProvider()
    )
    dexterity = resolve_saving_throw(
        fighter,
        AbilityKind.DEXTERITY,
        1,
        NoRollDiceProvider(),
        battlefield=battlefield,
        circumstantial_modifier=99,
    )
    assert strength.automatic_failure is True and strength.roll is None
    assert dexterity.automatic_failure is True and dexterity.roll is None
    assert strength.success is False and dexterity.success is False


def test_paralyzed_constitution_save_still_rolls_normally() -> None:
    fighter = paralyze(build_combatant_state(build_demo_fighter()))
    result = resolve_saving_throw(
        fighter, AbilityKind.CONSTITUTION, 10, FixedDiceProvider([10])
    )
    assert result.automatic_failure is False
    assert result.roll is not None
    assert result.roll.total == 14
    assert result.success is True


def test_attacks_against_paralyzed_target_have_advantage_but_nat_one_still_misses() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = paralyze(build_combatant_state(build_goblin_warrior()))
    event = resolve_attack(
        1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([1, 1]),
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.hit is False
    assert event.critical is False


def test_hit_within_five_feet_against_paralyzed_target_is_critical() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = paralyze(build_combatant_state(build_goblin_warrior()))
    event = resolve_attack(
        1, 1, fighter, goblin, fighter.template.weapon_attack, 5,
        FixedDiceProvider([10, 10, 4, 5]),
    )
    assert event.hit is True
    assert event.critical is True
    assert event.damage_roll is not None
    assert event.damage_roll.rolls == [4, 5]


def test_attack_beyond_five_feet_has_advantage_but_not_automatic_critical() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    goblin = paralyze(build_combatant_state(build_goblin_warrior()))
    shortbow = rogue.template.alternate_weapon_attacks[0]
    event = resolve_attack(
        1, 1, rogue, goblin, shortbow, 20,
        FixedDiceProvider([10, 10, 4, 3]),
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.hit is True
    assert event.critical is False


def test_paralyzed_melee_critical_doubles_rogue_sneak_attack_dice() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    goblin = paralyze(build_combatant_state(build_goblin_warrior()))
    event = resolve_attack(
        1, 1, rogue, goblin, rogue.template.weapon_attack, 5,
        FixedDiceProvider([10, 10, 3, 4, 2, 5]),
    )
    assert event.hit is True
    assert event.critical is True
    assert event.damage_roll is not None
    assert event.damage_roll.rolls == [3, 4, 2, 5]
    assert event.damage_roll.total == 17


def test_paralyzed_creature_cannot_make_opportunity_attack() -> None:
    fighter = paralyze(build_combatant_state(build_demo_fighter()))
    goblin = build_combatant_state(build_goblin_warrior())
    event = resolve_opportunity_attack(
        1, 1, fighter, goblin, 5, 35, FixedDiceProvider([20])
    )
    assert event is None
    assert fighter.reaction_available is True
