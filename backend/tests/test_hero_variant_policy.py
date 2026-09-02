from app.content.hero_variant_policy import all_hero_variant_families, hero_variant_family


def test_fighter_uses_one_champion_family_with_four_optimized_variants() -> None:
    family = hero_variant_family("fighter")
    assert family.hero_name == "Karnok Stoneward"
    assert family.subclass_id == "champion"
    assert family.branch_level == 3
    assert family.variant_ids == ("great-weapon", "sword-shield", "archer", "dual-wield")
    assert family.expected_variant_count == 4


def test_every_other_class_uses_three_variants_from_its_canonical_subclass() -> None:
    families = all_hero_variant_families()
    assert len(families) == 12
    assert sum(len(family.variant_ids) for family in families) == 37
    for family in families:
        if family.class_id != "fighter":
            assert family.expected_variant_count == 3
            assert len(family.variant_ids) == 3
        assert family.branch_level == 3
        assert family.subclass_id
        assert family.subclass_name
