"""Source-only tests for 2014 Succubus/Incubus Shapechanger arena-neutral classification."""
from __future__ import annotations

import pytest

from app.content.monster_source_2014 import load_source_monsters_2014
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014


def test_succubus_shapechanger_exact_source_match_is_arena_neutral():
    monsters = {m.id: m for m in load_source_monsters_2014()}
    succubus = monsters["succubus-incubus"]
    assert verified_arena_inert_trait_2014(succubus, "Shapechanger") is True


def test_succubus_shapechanger_mutated_source_fails_closed():
    monsters = {m.id: m for m in load_source_monsters_2014()}
    succubus = monsters["succubus-incubus"]
    original = succubus.source_traits
    succubus.source_traits = original.replace("Small or Medium", "Large")
    assert verified_arena_inert_trait_2014(succubus, "Shapechanger") is False
    succubus.source_traits = original


def test_other_shapechanger_unaffected():
    monsters = {m.id: m for m in load_source_monsters_2014()}
    imp = monsters["imp"]
    assert verified_arena_inert_trait_2014(imp, "Shapechanger") is True  # existing
