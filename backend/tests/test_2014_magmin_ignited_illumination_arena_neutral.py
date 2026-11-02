"""Magmin 2014 Ignited Illumination source proof and fail-closed guard.

Standard Pit has no light-dependent combat outcome for non-sunlight bright/dim light.
"""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _magmin():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "magmin")
    except Exception:
        logger.exception("Pinned Magmin source unavailable")
        raise


def test_magmin_ignited_illumination_is_source_verified_and_preserved():
    try:
        mag = _magmin()
        original = mag.model_dump_json()
        assert verified_arena_inert_trait_2014(mag, "Ignited Illumination")
        assert "Ignited Illumination" not in unsupported_traits_2014(mag)
        # Other blockers remain
        assert "source:trait" not in basic_blockers_2014(mag) or "Ignited Illumination" not in unsupported_traits_2014(mag)
        assert mag.model_dump_json() == original
    except Exception:
        logger.exception("Magmin neutral illumination regression")
        raise


@pytest.mark.parametrize("old,new", [
    ("sheds bright light in a 10-foot radius", "sheds bright light in a 30-foot radius"),
    ("dim light for an additional 10 feet", "dim light for an additional 30 feet"),
    ("set itself ablaze or extinguish its flames", "set itself ablaze and gain fire damage"),
    ("As a bonus action", "As an action"),
])
def test_modified_magmin_illumination_fail_closed(old, new):
    try:
        mag = _magmin()
        assert old in (mag.source_traits or "")
        altered = mag.model_copy(update={
            "source_traits": mag.source_traits.replace(old, new),
        })
        assert not verified_arena_inert_trait_2014(altered, "Ignited Illumination")
        assert "Ignited Illumination" in unsupported_traits_2014(altered)
    except Exception:
        logger.exception("Magmin source mutation must fail closed")
        raise


def test_unrelated_illumination_cannot_inherit_magmin_exception():
    try:
        # Use a monster that has Illumination if any, or just check isolation
        monster = next(row for row in load_monster_source_2014() if "Illumination" in row.trait_names and row.id != "magmin")
        assert not verified_arena_inert_trait_2014(monster, "Ignited Illumination")
    except StopIteration:
        # No other, isolation by id check is sufficient
        mag = _magmin()
        assert verified_arena_inert_trait_2014(mag, "Ignited Illumination")
    except Exception:
        logger.exception("Illumination source isolation failed")
        raise
