from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.ranger_subclass_overlay_data import RANGER_SUBCLASS_DELTA_DATA, RANGER_SUBCLASS_SPELLS


def test_ranger_family_has_three_real_sparse_subclass_progressions() -> None:
    assert set(RANGER_SUBCLASS_DELTA_DATA) == {"hunter", "gloom-stalker", "beastmaster"}
    assert tuple(RANGER_SUBCLASS_DELTA_DATA["hunter"]) == (3, 7, 11, 15)
    assert tuple(RANGER_SUBCLASS_DELTA_DATA["gloom-stalker"]) == (3, 5, 7, 9, 11, 13, 15, 17)
    assert tuple(RANGER_SUBCLASS_DELTA_DATA["beastmaster"]) == (3, 7, 11, 15)


def test_each_ranger_subclass_reuses_shared_ranger_features_without_hunter_leakage() -> None:
    hunter = canonical_combat_features("ranger", 15, "hunter")
    gloom = canonical_combat_features("ranger", 15, "gloom-stalker")
    beast = canonical_combat_features("ranger", 15, "beastmaster")
    assert all("extra-attack" in features for features in (hunter, gloom, beast))
    assert all("relentless-hunter" in features for features in (hunter, gloom, beast))
    assert "hunter-prey-colossus-slayer" in hunter
    assert "hunter-prey-colossus-slayer" not in gloom
    assert "hunter-prey-colossus-slayer" not in beast
    assert "gloom-stalker-stalkers-flurry" in gloom
    assert "beastmaster-bestial-fury" in beast


def test_gloom_stalker_spell_milestones_are_exact_sparse_subclass_data() -> None:
    assert RANGER_SUBCLASS_SPELLS["gloom-stalker"] == {
        3: ("disguise-self",),
        5: ("rope-trick",),
        9: ("fear",),
        13: ("greater-invisibility",),
        17: ("seeming",),
    }
    rows = RANGER_SUBCLASS_DELTA_DATA["gloom-stalker"]
    assert tuple(level for level in rows if "combat-spells" in str(rows[level])) == (3, 5, 9, 13, 17)
