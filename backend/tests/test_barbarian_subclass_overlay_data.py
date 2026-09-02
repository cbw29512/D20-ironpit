from app.content.barbarian_subclass_overlay_data import BARBARIAN_SUBCLASS_DELTA_DATA
from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.subclass_combat_overlays import subclass_combat_features


def test_barbarian_family_has_three_real_sparse_subclass_progressions() -> None:
    assert set(BARBARIAN_SUBCLASS_DELTA_DATA) == {
        "path-berserker", "path-wild-heart", "path-zealot",
    }
    for rows in BARBARIAN_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 6, 10, 14)


def test_wild_heart_and_zealot_reuse_the_barbarian_class_spine() -> None:
    wild_heart = canonical_combat_features("barbarian", 14, "path-wild-heart")
    zealot = canonical_combat_features("barbarian", 14, "path-zealot")
    assert "rage" in wild_heart and "rage" in zealot
    assert "extra-attack" in wild_heart and "extra-attack" in zealot
    assert "wild-heart-power-of-the-wilds" in wild_heart
    assert "zealot-rage-of-the-gods" in zealot
    assert "frenzy" not in wild_heart and "frenzy" not in zealot


def test_wild_heart_ritual_features_are_profile_truth_not_arena_features() -> None:
    assert "wild-heart-animal-speaker" not in subclass_combat_features("path-wild-heart", 3)
    assert "wild-heart-nature-speaker" not in subclass_combat_features("path-wild-heart", 10)
    assert BARBARIAN_SUBCLASS_DELTA_DATA["path-wild-heart"][3]["arena_ignored"] == (
        "wild-heart-animal-speaker",
    )
