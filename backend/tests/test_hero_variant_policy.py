from app.content.hero_variant_policy import TARGET_SUBCLASSES, all_hero_subclass_families, hero_subclass_family


def test_fighter_branches_once_into_four_subclass_specializations() -> None:
    family = hero_subclass_family("fighter")
    assert family.hero_name == "Karnok Stoneward"
    assert family.branch_level == 3
    assert family.target_subclass_ids == ("champion", "battle-master", "eldritch-knight", "psi-warrior")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_every_other_class_has_three_named_subclass_targets_without_fake_completion() -> None:
    families = all_hero_subclass_families()
    assert len(families) == 12
    assert set(TARGET_SUBCLASSES) == {family.class_id for family in families}
    for family in families:
        assert family.branch_level == 3
        assert family.target_subclass_ids
        assert family.audited_subclass_ids
        if family.class_id != "fighter":
            assert len(family.target_subclass_ids) == 3
            assert family.migration_complete is False


def test_caster_targets_are_subclasses_not_fake_fire_frost_build_clones() -> None:
    assert TARGET_SUBCLASSES["wizard"] == ("evoker", "illusionist", "abjurer")
    assert TARGET_SUBCLASSES["sorcerer"] == (
        "draconic-sorcery", "aberrant-sorcery", "clockwork-sorcery",
    )
    assert TARGET_SUBCLASSES["warlock"] == (
        "fiend-patron", "great-old-one-patron", "celestial-patron",
    )
