from app.content.audited_barbarian import build_rokhan_stonefury
from app.content.level_resources import (
    barbarian_rage_damage_bonus,
    barbarian_rage_uses,
    fighter_second_wind_uses,
    orc_adrenaline_rush_uses,
    proficiency_bonus,
)
from app.content.pregens import build_brom_ironmark, build_selene_asharrow


def _resource(template, resource_id: str):
    return next(item for item in template.resources if item.id == resource_id)


def test_barbarian_rage_uses_scale_with_level() -> None:
    expected = {
        1: 2, 2: 2, 3: 3, 5: 3, 6: 4, 11: 4,
        12: 5, 16: 5, 17: 6, 20: 6,
    }
    for level, uses in expected.items():
        assert barbarian_rage_uses(level) == uses


def test_barbarian_rage_damage_scales_with_level() -> None:
    assert barbarian_rage_damage_bonus(1) == 2
    assert barbarian_rage_damage_bonus(8) == 2
    assert barbarian_rage_damage_bonus(9) == 3
    assert barbarian_rage_damage_bonus(15) == 3
    assert barbarian_rage_damage_bonus(16) == 4
    assert barbarian_rage_damage_bonus(20) == 4


def test_fighter_second_wind_uses_scale_with_level() -> None:
    expected = {1: 2, 3: 2, 4: 3, 9: 3, 10: 4, 20: 4}
    for level, uses in expected.items():
        assert fighter_second_wind_uses(level) == uses


def test_proficiency_scaled_species_resource_uses_scale_with_level() -> None:
    for level, bonus in [(1, 2), (4, 2), (5, 3), (9, 4), (13, 5), (17, 6), (20, 6)]:
        assert proficiency_bonus(level) == bonus
        assert orc_adrenaline_rush_uses(level) == bonus


def test_current_pregens_receive_level_appropriate_resource_maxima() -> None:
    barbarian = build_rokhan_stonefury()
    assert _resource(barbarian, "rage").max_uses == barbarian_rage_uses(barbarian.level)
    assert _resource(barbarian, "adrenaline-rush").max_uses == orc_adrenaline_rush_uses(barbarian.level)
    for fighter in [build_brom_ironmark(), build_selene_asharrow()]:
        assert _resource(fighter, "second-wind").max_uses == fighter_second_wind_uses(fighter.level)


def test_level_resource_tables_fail_closed_outside_character_levels() -> None:
    for level in [0, 21]:
        for resolver in [barbarian_rage_uses, fighter_second_wind_uses, proficiency_bonus]:
            try:
                resolver(level)
            except ValueError:
                pass
            else:
                raise AssertionError(f"{resolver.__name__} accepted illegal level {level}")
