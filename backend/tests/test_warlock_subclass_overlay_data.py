from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.warlock_subclass_overlay_data import WARLOCK_SUBCLASS_DELTA_DATA


def test_warlock_family_has_three_real_sparse_patron_progressions() -> None:
    assert set(WARLOCK_SUBCLASS_DELTA_DATA) == {
        "fiend-patron", "great-old-one-patron", "celestial-patron",
    }
    for rows in WARLOCK_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 5, 6, 7, 9, 10, 14)


def test_each_patron_reuses_shared_pact_magic_without_fiend_leakage() -> None:
    fiend = canonical_combat_features("warlock", 14, "fiend-patron")
    great_old_one = canonical_combat_features("warlock", 14, "great-old-one-patron")
    celestial = canonical_combat_features("warlock", 14, "celestial-patron")
    assert all("pact-magic" in features for features in (fiend, great_old_one, celestial))
    assert all("eldritch-invocations" in features for features in (fiend, great_old_one, celestial))
    assert "hurl-through-hell" in fiend
    assert "hurl-through-hell" not in great_old_one
    assert "hurl-through-hell" not in celestial
    assert "create-thrall" in great_old_one
    assert "searing-vengeance" in celestial
