from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_saving_throw, saving_throw_bonus
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.rogue import build_demo_rogue
from app.domain.models import (
    AbilityKind,
    ActorVisibilityState,
    BattlefieldState,
    CoverLevel,
    RollMode,
)


class NoRollDiceProvider:
    def roll(self, sides: int) -> int:
        raise AssertionError(f"Voluntary failure must not roll d{sides}.")


def test_class_save_proficiencies_are_derived_from_template_data() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    rogue = build_combatant_state(build_demo_rogue())

    assert saving_throw_bonus(fighter, AbilityKind.STRENGTH) == 5
    assert saving_throw_bonus(fighter, AbilityKind.CONSTITUTION) == 4
    assert saving_throw_bonus(fighter, AbilityKind.DEXTERITY) == 1
    assert saving_throw_bonus(rogue, AbilityKind.DEXTERITY) == 5
    assert saving_throw_bonus(rogue, AbilityKind.INTELLIGENCE) == 3
    assert saving_throw_bonus(rogue, AbilityKind.WISDOM) == 2


def test_goblin_saves_match_srd_stat_block() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    assert saving_throw_bonus(goblin, AbilityKind.STRENGTH) == -1
    assert saving_throw_bonus(goblin, AbilityKind.DEXTERITY) == 2
    assert saving_throw_bonus(goblin, AbilityKind.CONSTITUTION) == 0
    assert saving_throw_bonus(goblin, AbilityKind.INTELLIGENCE) == 0
    assert saving_throw_bonus(goblin, AbilityKind.WISDOM) == -1
    assert saving_throw_bonus(goblin, AbilityKind.CHARISMA) == -1


def test_ordinary_save_has_no_automatic_failure_on_natural_one() -> None:
    fighter = build_combatant_state(build_demo_fighter())

    result = resolve_saving_throw(
        fighter, AbilityKind.STRENGTH, 6, FixedDiceProvider([1])
    )

    assert result.roll is not None
    assert result.roll.selected_roll == 1
    assert result.roll.total == 6
    assert result.success is True


def test_ordinary_save_has_no_automatic_success_on_natural_twenty() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    result = resolve_saving_throw(
        goblin, AbilityKind.DEXTERITY, 25, FixedDiceProvider([20])
    )

    assert result.roll is not None
    assert result.roll.total == 22
    assert result.success is False


def test_advantage_and_disadvantage_cancel_on_save() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    result = resolve_saving_throw(
        goblin,
        AbilityKind.WISDOM,
        10,
        FixedDiceProvider([11]),
        advantage_sources=1,
        disadvantage_sources=1,
    )

    assert result.roll is not None
    assert result.roll.mode is RollMode.NORMAL
    assert result.roll.total == 10
    assert result.success is True


def test_creature_can_choose_to_fail_save_without_rolling() -> None:
    goblin = build_combatant_state(build_goblin_warrior())

    result = resolve_saving_throw(
        goblin,
        AbilityKind.DEXTERITY,
        10,
        NoRollDiceProvider(),
        choose_failure=True,
    )

    assert result.roll is None
    assert result.success is False
    assert result.chosen_failure is True


def test_half_cover_adds_two_to_dexterity_save() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    battlefield = BattlefieldState(
        visibility_by_actor={
            goblin.template.id: ActorVisibilityState(cover=CoverLevel.HALF)
        }
    )

    result = resolve_saving_throw(
        goblin,
        AbilityKind.DEXTERITY,
        15,
        FixedDiceProvider([11]),
        battlefield=battlefield,
    )

    assert result.cover_bonus == 2
    assert result.roll is not None
    assert result.roll.total == 15
    assert result.success is True


def test_three_quarters_cover_adds_five_only_to_dexterity_save() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    battlefield = BattlefieldState(
        visibility_by_actor={
            fighter.template.id: ActorVisibilityState(cover=CoverLevel.THREE_QUARTERS)
        }
    )

    dex = resolve_saving_throw(
        fighter,
        AbilityKind.DEXTERITY,
        15,
        FixedDiceProvider([9]),
        battlefield=battlefield,
    )
    strength = resolve_saving_throw(
        fighter,
        AbilityKind.STRENGTH,
        15,
        FixedDiceProvider([9]),
        battlefield=battlefield,
    )

    assert dex.cover_bonus == 5
    assert dex.roll is not None and dex.roll.total == 15
    assert dex.success is True
    assert strength.cover_bonus == 0
    assert strength.roll is not None and strength.roll.total == 14
    assert strength.success is False
