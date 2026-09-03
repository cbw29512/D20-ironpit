from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.wizard_subclass_overlay_data import WIZARD_SUBCLASS_DELTA_DATA


def test_wizard_family_has_three_real_sparse_subclass_progressions() -> None:
    assert set(WIZARD_SUBCLASS_DELTA_DATA) == {"evoker", "illusionist", "abjurer"}
    for rows in WIZARD_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 6, 10, 14)


def test_each_wizard_subclass_reuses_shared_spellcasting_without_evoker_leakage() -> None:
    evoker = canonical_combat_features("wizard", 14, "evoker")
    illusionist = canonical_combat_features("wizard", 14, "illusionist")
    abjurer = canonical_combat_features("wizard", 14, "abjurer")
    assert all("wizard-spellcasting" in features for features in (evoker, illusionist, abjurer))
    assert all("arcane-recovery" in features for features in (evoker, illusionist, abjurer))
    assert "overchannel" in evoker
    assert "overchannel" not in illusionist
    assert "overchannel" not in abjurer
    assert "illusory-reality" in illusionist
    assert "spell-resistance" in abjurer
