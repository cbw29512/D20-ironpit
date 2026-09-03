from app.content.combat_build_variants import (
    COMBAT_BUILD_VARIANTS,
    combat_build_variants_for,
    get_combat_build_variant,
)
from app.content.druid_combat_build_variants import DRUID_COMBAT_BUILD_VARIANTS
from app.content.hero_progressions import CANONICAL_BUILD_ID, HERO_BY_CLASS


def test_legacy_build_registry_remains_complete_while_subclass_migration_runs() -> None:
    counts = {class_id: len(combat_build_variants_for(class_id)) for class_id in HERO_BY_CLASS}
    assert set(counts) == set(HERO_BY_CLASS)
    assert all(count >= 3 for count in counts.values())
    assert counts["fighter"] == 4
    assert sum(counts.values()) == 37
    assert len(COMBAT_BUILD_VARIANTS) == 37


def test_fighter_weapon_roles_are_now_owned_by_real_subclasses() -> None:
    expected = {
        "great-weapon": "champion",
        "dual-wield": "battle-master",
        "sword-shield": "eldritch-knight",
        "archer": "psi-warrior",
    }
    assert {
        variant.id: variant.required_subclass_id
        for variant in combat_build_variants_for("fighter")
    } == expected


def test_other_legacy_role_records_stay_planned_until_subclass_migration() -> None:
    expected = {
        "barbarian": {"great-weapon", "weapon-shield", "dual-wield"},
        "monk": {"unarmed-offense", "weapon-monk", "defensive-mobile"},
        "rogue": {"duelist", "dual-wield", "ranged"},
    }
    for class_id, build_ids in expected.items():
        assert {variant.id for variant in combat_build_variants_for(class_id)} == build_ids


def test_barbarian_weapon_roles_are_owned_by_real_subclasses() -> None:
    assert {
        variant.id: variant.required_subclass_id
        for variant in combat_build_variants_for("barbarian")
    } == {
        "great-weapon": "path-berserker",
        "weapon-shield": "path-wild-heart",
        "dual-wield": "path-zealot",
    }


def test_monk_roles_are_owned_by_real_subclasses() -> None:
    assert {
        variant.id: variant.required_subclass_id
        for variant in combat_build_variants_for("monk")
    } == {
        "unarmed-offense": "warrior-open-hand",
        "weapon-monk": "warrior-shadow",
        "defensive-mobile": "warrior-elements",
    }


def test_paladin_roles_are_owned_by_real_subclasses() -> None:
    assert {
        variant.id: variant.required_subclass_id
        for variant in combat_build_variants_for("paladin")
    } == {
        "great-weapon": "oath-vengeance",
        "sword-shield": "oath-devotion",
        "support-healer": "oath-ancients",
    }


def test_ranger_roles_are_owned_by_real_subclasses() -> None:
    assert {
        variant.id: variant.required_subclass_id
        for variant in combat_build_variants_for("ranger")
    } == {
        "archer": "gloom-stalker",
        "dual-wield": "beastmaster",
        "sword-shield": "hunter",
    }


def test_legacy_caster_role_records_remain_migration_inputs_not_subclass_clones() -> None:
    expected = {
        "wizard": {"fire-damage", "frost-control", "mixed-arcane"},
        "sorcerer": {"fire-damage", "frost-control", "mixed-arcane"},
        "warlock": {"blaster", "controller", "blade-hybrid"},
        "bard": {"support-healer", "controller", "battle-bard"},
        "cleric": {"healer", "war-priest", "divine-offense"},
        "druid": {"land-damage", "healer", "moon-melee"},
    }
    for class_id, build_ids in expected.items():
        assert {variant.id for variant in combat_build_variants_for(class_id)} == build_ids


def test_every_legacy_record_reuses_one_class_progression_spine() -> None:
    for (class_id, build_id), variant in COMBAT_BUILD_VARIANTS.items():
        assert (variant.class_id, variant.id) == (class_id, build_id)
        assert variant.shared_progression_id == f"{class_id}-1-20"
        assert variant.status == "planned"


def test_fighter_specialization_records_are_fail_closed_until_subclass_compilers_exist() -> None:
    champion = get_combat_build_variant("fighter", "great-weapon")
    battle_master = get_combat_build_variant("fighter", "dual-wield")
    eldritch_knight = get_combat_build_variant("fighter", "sword-shield")
    psi_warrior = get_combat_build_variant("fighter", "archer")
    assert champion.required_subclass_id == "champion"
    assert battle_master.required_subclass_id == "battle-master"
    assert eldritch_knight.required_subclass_id == "eldritch-knight"
    assert psi_warrior.required_subclass_id == "psi-warrior"
    assert all(item.status == "planned" for item in (champion, battle_master, eldritch_knight, psi_warrior))
    assert CANONICAL_BUILD_ID == "canonical"


def test_subclass_specific_druid_records_remain_explicit() -> None:
    land = get_combat_build_variant("druid", "land-damage")
    moon = get_combat_build_variant("druid", "moon-melee")
    assert land.required_subclass_id == "circle-land"
    assert moon.required_subclass_id == "circle-moon"
    assert "RAW audit" in moon.notes


def test_druid_compatibility_view_has_one_shared_source_of_truth() -> None:
    assert set(DRUID_COMBAT_BUILD_VARIANTS) == {"land-damage", "healer", "moon-melee"}
    for build_id, variant in DRUID_COMBAT_BUILD_VARIANTS.items():
        assert variant is get_combat_build_variant("druid", build_id)


def test_build_registry_does_not_change_public_certification_key() -> None:
    assert CANONICAL_BUILD_ID == "canonical"
    assert all(build_id != CANONICAL_BUILD_ID for _, build_id in COMBAT_BUILD_VARIANTS)
