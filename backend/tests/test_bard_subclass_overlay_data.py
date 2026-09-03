from app.content.canonical_class_combat_spines import canonical_base_class_features, canonical_combat_features
from app.content.bard_subclass_overlay_data import BARD_SUBCLASS_DELTA_DATA


def test_bard_family_has_three_real_sparse_college_progressions() -> None:
    assert set(BARD_SUBCLASS_DELTA_DATA) == {"college-lore", "college-valor", "college-glamour"}
    for rows in BARD_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 6, 14)


def test_bard_base_and_college_features_are_independent() -> None:
    base = canonical_base_class_features("bard", 14)
    lore = canonical_combat_features("bard", 14, "college-lore")
    valor = canonical_combat_features("bard", 14, "college-valor")
    glamour = canonical_combat_features("bard", 14, "college-glamour")
    assert "bardic-inspiration" in base
    assert "cutting-words" not in base and "cutting-words" in lore
    assert "battle-magic" in valor
    assert "unbreakable-majesty" in glamour
