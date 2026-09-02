from app.content.hero_variant_policy import all_hero_subclass_families, hero_subclass_family


def test_fighter_branches_once_into_four_subclass_specializations() -> None:
    family = hero_subclass_family("fighter")
    assert family.hero_name == "Karnok Stoneward"
    assert family.branch_level == 3
    assert family.subclass_ids == ("champion", "battle-master", "eldritch-knight", "psi-warrior")
    assert family.target_subclass_count == 4
    assert family.migration_complete is True


def test_other_classes_target_three_subclasses_without_fake_variant_counts() -> None:
    families = all_hero_subclass_families()
    assert len(families) == 12
    for family in families:
        assert family.branch_level == 3
        assert family.subclass_ids
        if family.class_id != "fighter":
            assert family.target_subclass_count == 3
            assert family.migration_complete is False
