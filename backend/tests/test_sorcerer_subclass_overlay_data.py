from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.sorcerer_subclass_overlay_data import SORCERER_SUBCLASS_DELTA_DATA


def test_sorcerer_family_has_three_real_sparse_subclass_progressions() -> None:
    assert set(SORCERER_SUBCLASS_DELTA_DATA) == {
        "draconic-sorcery", "aberrant-sorcery", "clockwork-sorcery",
    }
    for rows in SORCERER_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 6, 14, 18)


def test_each_sorcerer_subclass_reuses_shared_sorcery_without_draconic_leakage() -> None:
    draconic = canonical_combat_features("sorcerer", 18, "draconic-sorcery")
    aberrant = canonical_combat_features("sorcerer", 18, "aberrant-sorcery")
    clockwork = canonical_combat_features("sorcerer", 18, "clockwork-sorcery")
    assert all("innate-sorcery" in features for features in (draconic, aberrant, clockwork))
    assert all("font-of-magic" in features for features in (draconic, aberrant, clockwork))
    assert "dragon-companion" in draconic
    assert "dragon-companion" not in aberrant
    assert "dragon-companion" not in clockwork
    assert "warping-implosion" in aberrant
    assert "clockwork-cavalcade" in clockwork
