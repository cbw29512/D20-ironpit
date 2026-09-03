from app.content.canonical_class_combat_spines import canonical_base_class_features
from app.content.cleric_subclass_overlay_data import CLERIC_DOMAIN_SPELLS, CLERIC_SUBCLASS_DELTA_DATA
from app.content.subclass_combat_overlays import subclass_combat_features


def test_cleric_domains_are_sparse_rows_at_the_domain_feature_levels() -> None:
    assert set(CLERIC_SUBCLASS_DELTA_DATA) == {"life-domain", "light-domain", "war-domain"}
    for rows in CLERIC_SUBCLASS_DELTA_DATA.values():
        assert tuple(rows) == (3, 6, 17)


def test_each_cleric_domain_reuses_one_base_spine_without_life_leakage() -> None:
    base = set(canonical_base_class_features("cleric", 20))
    assert {"disciple-of-life", "preserve-life", "supreme-healing"}.isdisjoint(base)
    assert "corona-of-light" in subclass_combat_features("light-domain", 17)
    assert "avatar-of-battle" in subclass_combat_features("war-domain", 17)


def test_domain_spell_tables_are_exact_and_level_gated() -> None:
    assert set(CLERIC_DOMAIN_SPELLS) == {"life-domain", "light-domain", "war-domain"}
    for spells in CLERIC_DOMAIN_SPELLS.values():
        assert tuple(spells) == (3, 5, 7, 9)
        assert len(spells[3]) == 4
        assert all(len(spells[level]) == 2 for level in (5, 7, 9))
    assert CLERIC_DOMAIN_SPELLS["light-domain"][5] == ("daylight", "fireball")
    assert CLERIC_DOMAIN_SPELLS["war-domain"][9] == ("hold-monster", "steel-wind-strike")
