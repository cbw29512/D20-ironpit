from app.content.canonical_class_combat_spines import canonical_base_class_features
from app.content.druid_subclass_overlay_data import DRUID_SUBCLASS_DELTA_DATA, DRUID_SUBCLASS_SPELLS
from app.content.subclass_combat_overlays import subclass_combat_features


def test_druid_circles_are_sparse_rows_at_subclass_feature_levels() -> None:
    assert set(DRUID_SUBCLASS_DELTA_DATA) == {"circle-land", "circle-moon", "circle-sea"}
    for rows in DRUID_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 6, 10, 14)


def test_each_druid_circle_reuses_one_base_spine_without_land_leakage() -> None:
    base = set(canonical_base_class_features("druid", 20))
    assert {"lands-aid", "natural-recovery", "natures-ward-fire", "natures-sanctuary"}.isdisjoint(base)
    assert "lunar-form" in subclass_combat_features("circle-moon", 14)
    assert "oceanic-gift" in subclass_combat_features("circle-sea", 14)


def test_circle_spell_tables_are_exact_and_level_gated() -> None:
    assert set(DRUID_SUBCLASS_SPELLS) == {"circle-land", "circle-moon", "circle-sea"}
    for spells in DRUID_SUBCLASS_SPELLS.values():
        assert tuple(spells) == (3, 5, 7, 9)
    assert DRUID_SUBCLASS_SPELLS["circle-land"] == {
        3: ("blur", "burning-hands", "fire-bolt"),
        5: ("fireball",), 7: ("blight",), 9: ("wall-of-stone",),
    }
    assert DRUID_SUBCLASS_SPELLS["circle-moon"][3] == ("cure-wounds", "moonbeam", "starry-wisp")
    assert DRUID_SUBCLASS_SPELLS["circle-sea"][9] == ("conjure-elemental", "hold-monster")
