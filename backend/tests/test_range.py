import pytest

from app.combat.range import resolve_attack_roll_mode
from app.content.equipment import build_longsword, build_shortbow
from app.domain.models import RollMode


def test_melee_weapon_is_normal_within_reach() -> None:
    assert resolve_attack_roll_mode(build_longsword(), 5) is RollMode.NORMAL


def test_melee_weapon_cannot_target_beyond_reach() -> None:
    with pytest.raises(ValueError, match="outside melee reach"):
        resolve_attack_roll_mode(build_longsword(), 10)


def test_shortbow_is_normal_inside_normal_range_when_not_threatened() -> None:
    assert (
        resolve_attack_roll_mode(build_shortbow(), 60, close_enemy_active=False)
        is RollMode.NORMAL
    )


def test_shortbow_has_disadvantage_beyond_normal_range() -> None:
    assert (
        resolve_attack_roll_mode(build_shortbow(), 100, close_enemy_active=False)
        is RollMode.DISADVANTAGE
    )


def test_shortbow_has_disadvantage_in_close_combat() -> None:
    assert resolve_attack_roll_mode(build_shortbow(), 5) is RollMode.DISADVANTAGE


def test_shortbow_cannot_target_beyond_long_range() -> None:
    with pytest.raises(ValueError, match="beyond long range"):
        resolve_attack_roll_mode(build_shortbow(), 321, close_enemy_active=False)


def test_advantage_cancels_long_range_disadvantage() -> None:
    assert (
        resolve_attack_roll_mode(
            build_shortbow(),
            100,
            advantage_sources=1,
            close_enemy_active=False,
        )
        is RollMode.NORMAL
    )
