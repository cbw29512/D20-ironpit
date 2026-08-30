import pytest

from app.content.movement_modes import parse_movement_modes, standard_arena_closing_speed


def test_bat_preserves_walk_and_fly_speeds() -> None:
    assert parse_movement_modes("5 ft., Fly 30 ft.") == {"walk": 5, "fly": 30}
    assert standard_arena_closing_speed("5 ft., Fly 30 ft.") == 30


def test_black_bear_preserves_climb_and_swim_without_using_them_as_flat_pit_speed() -> None:
    speeds = parse_movement_modes("30 ft., Climb 30 ft., Swim 30 ft.")
    assert speeds == {"walk": 30, "climb": 30, "swim": 30}
    assert standard_arena_closing_speed("30 ft., Climb 30 ft., Swim 30 ft.") == 30


def test_fly_speed_can_legally_be_faster_than_walk_in_open_pit() -> None:
    assert standard_arena_closing_speed("10 ft., Fly 60 ft.") == 60


def test_swim_speed_is_not_available_without_water() -> None:
    assert standard_arena_closing_speed("20 ft., Swim 40 ft.") == 20


def test_unknown_movement_component_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown movement mode"):
        parse_movement_modes("30 ft., Teleport 60 ft.")
