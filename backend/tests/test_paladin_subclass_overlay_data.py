from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.paladin_subclass_overlay_data import PALADIN_OATH_SPELLS, PALADIN_SUBCLASS_DELTA_DATA


def test_paladin_family_has_three_real_sparse_oath_progressions() -> None:
    assert set(PALADIN_SUBCLASS_DELTA_DATA) == {
        "oath-devotion", "oath-vengeance", "oath-ancients",
    }
    for rows in PALADIN_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 5, 7, 9, 13, 15, 17, 20)


def test_each_oath_reuses_shared_paladin_features_without_devotion_leakage() -> None:
    devotion = canonical_combat_features("paladin", 15, "oath-devotion")
    vengeance = canonical_combat_features("paladin", 15, "oath-vengeance")
    ancients = canonical_combat_features("paladin", 15, "oath-ancients")
    assert all("aura-of-protection" in features for features in (devotion, vengeance, ancients))
    assert "sacred-weapon" in devotion
    assert "sacred-weapon" not in vengeance
    assert "sacred-weapon" not in ancients
    assert "vow-of-enmity" in vengeance
    assert "natures-wrath" in ancients
    assert "abjure-foes" in devotion
    assert "abjure-foes" in vengeance
    assert "abjure-foes" in ancients


def test_oath_spell_milestones_remain_sparse_subclass_data() -> None:
    for oath_id, prefix in (
        ("oath-devotion", "devotion"),
        ("oath-vengeance", "vengeance"),
        ("oath-ancients", "ancients"),
    ):
        rows = PALADIN_SUBCLASS_DELTA_DATA[oath_id]
        assert tuple(level for level in rows if f"{prefix}-combat-spells" in str(rows[level])) == (
            3, 5, 9, 13, 17,
        )
        assert tuple(PALADIN_OATH_SPELLS[oath_id]) == (3, 5, 9, 13, 17)
        assert all(len(spells) == 2 for spells in PALADIN_OATH_SPELLS[oath_id].values())


def test_oath_spell_packages_record_the_exact_2024_choices() -> None:
    assert PALADIN_OATH_SPELLS["oath-devotion"][3] == (
        "protection-from-evil-and-good", "shield-of-faith",
    )
    assert PALADIN_OATH_SPELLS["oath-vengeance"][17] == ("hold-monster", "scrying")
    assert PALADIN_OATH_SPELLS["oath-ancients"][13] == ("ice-storm", "stoneskin")
