import logging

import pytest

from app.content.movement_modes import (
    movement_source_issues,
    parse_movement_modes,
    parse_movement_profile,
    standard_arena_closing_speed,
)

logger = logging.getLogger(__name__)


def test_bat_preserves_walk_and_fly_speeds() -> None:
    try:
        assert parse_movement_modes("5 ft., Fly 30 ft.") == {"walk": 5, "fly": 30}
        profile = parse_movement_profile("5 ft., Fly 30 ft.")
        assert profile.walk_ft == 5
        assert profile.fly_ft == 30
        assert profile.hover is False
        assert standard_arena_closing_speed("5 ft., Fly 30 ft.") == 30
    except Exception:
        logger.exception("Bat walk/fly movement regression failed.")
        raise


def test_black_bear_preserves_climb_and_swim_fingerprint() -> None:
    try:
        speeds = parse_movement_modes("30 ft., Climb 30 ft., Swim 30 ft.")
        assert speeds == {"walk": 30, "climb": 30, "swim": 30}
        profile = parse_movement_profile("30 ft., Climb 30 ft., Swim 30 ft.")
        assert profile.climb_ft == 30
        assert profile.swim_ft == 30
        assert standard_arena_closing_speed("30 ft., Climb 30 ft., Swim 30 ft.") == 30
    except Exception:
        logger.exception("Black Bear movement fingerprint regression failed.")
        raise


def test_burrow_and_hover_are_retained_in_complete_fingerprint() -> None:
    try:
        profile = parse_movement_profile("20 ft., Burrow 10 ft., Fly 40 ft. (Hover)")
        assert profile.burrow_ft == 10
        assert profile.fly_ft == 40
        assert profile.hover is True
    except Exception:
        logger.exception("Burrow/hover movement fingerprint regression failed.")
        raise


def test_fly_speed_can_legally_be_faster_than_walk_in_open_pit() -> None:
    try:
        assert standard_arena_closing_speed("10 ft., Fly 60 ft.") == 60
    except Exception:
        logger.exception("Fly source-speed regression failed.")
        raise


def test_swim_speed_is_not_reinterpreted_as_generic_speed() -> None:
    try:
        assert standard_arena_closing_speed("5 ft., Swim 60 ft.") == 5
        assert standard_arena_closing_speed("20 ft., Swim 40 ft.") == 20
    except Exception:
        logger.exception("Swim source-speed separation regression failed.")
        raise


def test_form_only_speed_stays_out_of_default_runtime_profile() -> None:
    try:
        source = "30 ft., 40 ft. (wolf form only)"
        assert parse_movement_modes(source) == {"walk": 30}
        assert standard_arena_closing_speed(source) == 30
        assert movement_source_issues(source) == ["movement-form-source-unmodeled"]
    except Exception:
        logger.exception("Conditional form movement regression failed.")
        raise


def test_truncated_form_parenthetical_is_safe_and_blocks_certification() -> None:
    try:
        source = "30 ft., 40 ft. (bear form only), Climb 30 ft. (bear"
        assert parse_movement_modes(source) == {"walk": 30}
        assert movement_source_issues(source) == [
            "movement-form-source-unmodeled",
            "movement-parenthetical-source-malformed",
        ]
    except Exception:
        logger.exception("Malformed conditional movement regression failed.")
        raise


def test_gm_choice_movement_is_not_silently_selected() -> None:
    try:
        source = "20 ft., Climb or Fly 20 ft. (GM’s choice)"
        assert parse_movement_modes(source) == {"walk": 20}
        assert standard_arena_closing_speed(source) == 20
        assert movement_source_issues(source) == ["movement-choice-source-unmodeled"]
    except Exception:
        logger.exception("GM-choice movement fail-closed regression failed.")
        raise


def test_unknown_movement_component_fails_closed() -> None:
    try:
        with pytest.raises(ValueError, match="Unknown movement mode"):
            parse_movement_modes("30 ft., Teleport 60 ft.")
    except Exception:
        logger.exception("Unknown movement component fail-closed regression failed.")
        raise


def test_hover_without_flight_fails_closed() -> None:
    try:
        with pytest.raises(ValueError, match="Hover is printed without a Fly speed"):
            parse_movement_profile("30 ft. (Hover)")
    except Exception:
        logger.exception("Hover-without-flight fail-closed regression failed.")
        raise
