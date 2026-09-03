from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.rogue_subclass_overlay_data import ROGUE_SUBCLASS_DELTA_DATA


def test_rogue_family_has_three_real_sparse_subclass_progressions() -> None:
    assert set(ROGUE_SUBCLASS_DELTA_DATA) == {"thief", "assassin", "arcane-trickster"}
    for rows in ROGUE_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 9, 13, 17)


def test_each_rogue_subclass_reuses_shared_rogue_features_without_thief_leakage() -> None:
    thief = canonical_combat_features("rogue", 17, "thief")
    assassin = canonical_combat_features("rogue", 17, "assassin")
    trickster = canonical_combat_features("rogue", 17, "arcane-trickster")
    assert all("sneak-attack" in features for features in (thief, assassin, trickster))
    assert all("cunning-strike" in features for features in (thief, assassin, trickster))
    assert "thief-fast-hands" in thief
    assert "thief-fast-hands" not in assassin
    assert "thief-fast-hands" not in trickster
    assert "assassin-death-strike" in assassin
    assert "arcane-trickster-spell-thief" in trickster
