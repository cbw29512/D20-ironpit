from app.combat.dice import FixedDiceProvider
from app.combat.rolls import attack_roll_hits, resolve_roll_mode, roll_d20
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


def test_attack_hit_rule_is_one_shared_primitive() -> None:
    assert attack_roll_hits(1, 99, 10) is False
    assert attack_roll_hits(20, 1, 99) is True
    assert attack_roll_hits(12, 17, 17) is True
    assert attack_roll_hits(12, 16, 17) is False
