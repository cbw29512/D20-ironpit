from __future__ import annotations

from app.content.druid_2014_progression import druid_2014_features
from app.content.druid_land_2014_progression import (
    compiled_land_druid_2014_features,
    land_druid_2014_features,
)


def test_base_druid_spine_excludes_land_subclass_features() -> None:
    base = set(druid_2014_features(20))
    assert {
        "spellcasting",
        "druidic",
        "wild-shape",
        "druid-circle",
        "wild-shape-improvement",
        "timeless-body",
        "beast-spells",
        "archdruid",
    } <= base
    assert {
        "bonus-cantrip",
        "natural-recovery",
        "circle-spells-2",
        "circle-spells-3",
        "circle-spells-4",
        "circle-spells-5",
        "lands-stride",
        "natures-ward",
        "natures-sanctuary",
    }.isdisjoint(base)


def test_land_overlay_contains_only_land_features() -> None:
    overlay = set(land_druid_2014_features(20))
    assert overlay == {
        "bonus-cantrip",
        "natural-recovery",
        "circle-spells-2",
        "circle-spells-3",
        "circle-spells-4",
        "circle-spells-5",
        "lands-stride",
        "natures-ward",
        "natures-sanctuary",
    }


def test_compiled_land_druid_inherits_base_and_subclass_progressions() -> None:
    compiled = set(compiled_land_druid_2014_features(20))
    assert "wild-shape" in compiled
    assert "beast-spells" in compiled
    assert "natural-recovery" in compiled
    assert "natures-sanctuary" in compiled
