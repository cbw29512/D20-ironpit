import pytest

from app.content.standard_magic_gear import (
    higher_level_magic_item_budget,
    standard_martial_enhancements,
)


def test_official_higher_level_magic_item_budgets() -> None:
    assert higher_level_magic_item_budget(1) == (0, 0, 0, 0)
    assert higher_level_magic_item_budget(4) == (1, 0, 0, 0)
    assert higher_level_magic_item_budget(5) == (1, 1, 0, 0)
    assert higher_level_magic_item_budget(10) == (1, 1, 0, 0)
    assert higher_level_magic_item_budget(11) == (2, 3, 1, 0)
    assert higher_level_magic_item_budget(16) == (2, 3, 1, 0)
    assert higher_level_magic_item_budget(17) == (2, 4, 3, 1)
    assert higher_level_magic_item_budget(20) == (2, 4, 3, 1)


def test_standard_martial_magic_scaling_stays_simple() -> None:
    low = standard_martial_enhancements(4, uses_shield=True)
    assert (low.weapon_bonus, low.armor_bonus, low.shield_bonus, low.utility_items) == (0, 0, 0, 0)

    tier_two = standard_martial_enhancements(5, uses_shield=True)
    assert (tier_two.weapon_bonus, tier_two.armor_bonus, tier_two.shield_bonus) == (1, 0, 0)

    tier_three = standard_martial_enhancements(11, uses_shield=True)
    assert (tier_three.weapon_bonus, tier_three.armor_bonus, tier_three.shield_bonus) == (2, 0, 1)

    tier_four = standard_martial_enhancements(17, uses_shield=True)
    assert (tier_four.weapon_bonus, tier_four.armor_bonus, tier_four.shield_bonus) == (3, 1, 1)


def test_two_handed_martial_does_not_receive_unused_magic_shield() -> None:
    assert standard_martial_enhancements(16, uses_shield=False).shield_bonus == 0
    assert standard_martial_enhancements(20, uses_shield=False).shield_bonus == 0


def test_invalid_level_fails_closed() -> None:
    with pytest.raises(ValueError):
        higher_level_magic_item_budget(0)
    with pytest.raises(ValueError):
        standard_martial_enhancements(21, uses_shield=True)
