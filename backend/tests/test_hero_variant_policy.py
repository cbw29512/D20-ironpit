from app.content.hero_variant_policy import TARGET_SUBCLASSES, all_hero_subclass_families, hero_subclass_family


def test_fighter_branches_once_into_four_subclass_specializations() -> None:
    family = hero_subclass_family("fighter")
    assert family.hero_name == "Karnok Stoneward"
    assert family.branch_level == 3
    assert family.target_subclass_ids == ("champion", "battle-master", "eldritch-knight", "psi-warrior")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_barbarian_branches_once_into_three_subclass_specializations() -> None:
    family = hero_subclass_family("barbarian")
    assert family.target_subclass_ids == ("path-berserker", "path-wild-heart", "path-zealot")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_monk_branches_once_into_three_subclass_specializations() -> None:
    family = hero_subclass_family("monk")
    assert family.target_subclass_ids == ("warrior-open-hand", "warrior-shadow", "warrior-elements")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_paladin_branches_once_into_three_oath_specializations() -> None:
    family = hero_subclass_family("paladin")
    assert family.target_subclass_ids == ("oath-devotion", "oath-vengeance", "oath-ancients")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_ranger_branches_once_into_three_subclass_specializations() -> None:
    family = hero_subclass_family("ranger")
    assert family.target_subclass_ids == ("hunter", "gloom-stalker", "beastmaster")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_rogue_branches_once_into_three_subclass_specializations() -> None:
    family = hero_subclass_family("rogue")
    assert family.target_subclass_ids == ("thief", "assassin", "arcane-trickster")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_wizard_branches_once_into_three_subclass_specializations() -> None:
    family = hero_subclass_family("wizard")
    assert family.target_subclass_ids == ("evoker", "illusionist", "abjurer")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_sorcerer_branches_once_into_three_subclass_specializations() -> None:
    family = hero_subclass_family("sorcerer")
    assert family.target_subclass_ids == (
        "draconic-sorcery", "aberrant-sorcery", "clockwork-sorcery",
    )
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_warlock_branches_once_into_three_patron_specializations() -> None:
    family = hero_subclass_family("warlock")
    assert family.target_subclass_ids == (
        "fiend-patron", "great-old-one-patron", "celestial-patron",
    )
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_bard_branches_once_into_three_college_specializations() -> None:
    family = hero_subclass_family("bard")
    assert family.target_subclass_ids == ("college-lore", "college-valor", "college-glamour")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_cleric_branches_once_into_three_domain_specializations() -> None:
    family = hero_subclass_family("cleric")
    assert family.target_subclass_ids == ("life-domain", "light-domain", "war-domain")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_druid_branches_once_into_three_circle_specializations() -> None:
    family = hero_subclass_family("druid")
    assert family.target_subclass_ids == ("circle-land", "circle-moon", "circle-sea")
    assert family.audited_subclass_ids == family.target_subclass_ids
    assert family.migration_complete is True


def test_every_roster_class_has_its_complete_named_subclass_family() -> None:
    families = all_hero_subclass_families()
    assert len(families) == 12
    assert set(TARGET_SUBCLASSES) == {family.class_id for family in families}
    for family in families:
        assert family.branch_level == 3
        assert family.target_subclass_ids
        assert family.audited_subclass_ids
        assert len(family.target_subclass_ids) == (4 if family.class_id == "fighter" else 3)
        assert family.migration_complete is True


def test_caster_targets_are_subclasses_not_fake_fire_frost_build_clones() -> None:
    assert TARGET_SUBCLASSES["wizard"] == ("evoker", "illusionist", "abjurer")
    assert TARGET_SUBCLASSES["sorcerer"] == (
        "draconic-sorcery", "aberrant-sorcery", "clockwork-sorcery",
    )
    assert TARGET_SUBCLASSES["warlock"] == (
        "fiend-patron", "great-old-one-patron", "celestial-patron",
    )
