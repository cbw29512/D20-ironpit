from app.combat.dice import FixedDiceProvider
from app.combat.rolls import resolve_roll_mode, roll_d20
from app.domain.models import RollMode


def test_advantage_keeps_higher_d20() -> None:
    result = roll_d20(FixedDiceProvider([3, 17]), modifier=5, mode=RollMode.ADVANTAGE)

    assert result.rolls == [3, 17]
    assert result.selected_roll == 17
    assert result.total == 22
    assert result.mode is RollMode.ADVANTAGE


def test_disadvantage_keeps_lower_d20() -> None:
    result = roll_d20(FixedDiceProvider([18, 4]), modifier=2, mode=RollMode.DISADVANTAGE)

    assert result.rolls == [18, 4]
    assert result.selected_roll == 4
    assert result.total == 6
    assert result.mode is RollMode.DISADVANTAGE


def test_advantage_and_disadvantage_cancel_regardless_of_source_count() -> None:
    assert resolve_roll_mode(advantage_sources=3, disadvantage_sources=1) is RollMode.NORMAL
    assert resolve_roll_mode(advantage_sources=2, disadvantage_sources=0) is RollMode.ADVANTAGE
    assert resolve_roll_mode(advantage_sources=0, disadvantage_sources=2) is RollMode.DISADVANTAGE
