"""Imp 2014 movement-only Shapechanger source proof and fail-closed guard."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _imp():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "imp")
    except Exception:
        logger.exception("Pinned Imp source unavailable")
        raise


def test_imp_shapechange_is_source_verified_and_preserved():
    try:
        imp = _imp()
        original = imp.model_dump_json()
        assert verified_arena_inert_trait_2014(imp, "Shapechanger")
        assert "Shapechanger" not in unsupported_traits_2014(imp)
        assert not basic_blockers_2014(imp)
        assert imp.model_dump_json() == original
    except Exception:
        logger.exception("Imp neutral shapechange regression")
        raise


@pytest.mark.parametrize("old,new", [
    ("Its statistics are the same in each form", "Its AC increases in beast form"),
    ("except for the speed changes noted", "except for speed and attack damage"),
    ("fly 60 ft.", "fly 80 ft."),
    ("climb 20 ft.", "climb 40 ft."),
    ("It reverts to its true form if it dies.", "It keeps its beast form if it dies."),
])
def test_modified_imp_form_effects_fail_closed(old, new):
    try:
        imp = _imp()
        assert old in (imp.source_traits or "")
        altered = imp.model_copy(update={
            "source_traits": imp.source_traits.replace(old, new),
        })
        assert not verified_arena_inert_trait_2014(altered, "Shapechanger")
        assert "Shapechanger" in unsupported_traits_2014(altered)
        assert "source:trait" in basic_blockers_2014(altered)
    except Exception:
        logger.exception("Imp source mutation must fail closed")
        raise


def test_unrelated_shapechanger_cannot_inherit_imp_exception():
    try:
        monster = next(row for row in load_monster_source_2014() if row.id == "mimic")
        assert not verified_arena_inert_trait_2014(monster, "Shapechanger")
        assert "Shapechanger" in unsupported_traits_2014(monster)
    except Exception:
        logger.exception("Shapechanger source isolation failed")
        raise
