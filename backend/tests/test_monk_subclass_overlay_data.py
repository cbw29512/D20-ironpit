from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.monk_subclass_overlay_data import MONK_SUBCLASS_DELTA_DATA
from app.content.subclass_combat_overlays import subclass_combat_features


def test_monk_family_has_three_real_sparse_subclass_progressions() -> None:
    assert set(MONK_SUBCLASS_DELTA_DATA) == {
        "warrior-open-hand", "warrior-shadow", "warrior-elements",
    }
    for rows in MONK_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 6, 11, 17)


def test_shadow_and_elements_reuse_the_monk_class_spine_without_open_hand_leakage() -> None:
    shadow = canonical_combat_features("monk", 17, "warrior-shadow")
    elements = canonical_combat_features("monk", 17, "warrior-elements")
    assert "martial-arts" in shadow and "martial-arts" in elements
    assert "extra-attack" in shadow and "extra-attack" in elements
    assert "cloak-of-shadows" in shadow
    assert "elemental-epitome" in elements
    assert "open-hand-technique" not in shadow and "open-hand-technique" not in elements


def test_manipulate_elements_is_profile_truth_not_an_arena_feature() -> None:
    assert "manipulate-elements" not in subclass_combat_features("warrior-elements", 3)
    assert MONK_SUBCLASS_DELTA_DATA["warrior-elements"][3]["arena_ignored"] == (
        "manipulate-elements",
    )
