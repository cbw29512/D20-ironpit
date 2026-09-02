from app.content.combat_build_variants import (
    COMBAT_BUILD_VARIANTS,
    combat_build_variants_for,
    get_combat_build_variant,
)
from app.content.druid_combat_build_variants import DRUID_COMBAT_BUILD_VARIANTS
from app.content.hero_progressions import CANONICAL_BUILD_ID, HERO_BY_CLASS


def test_every_canonical_class_has_at_least_three_combat_builds() -> None:
    counts = {class_id: len(combat_build_variants_for(class_id)) for class_id in HERO_BY_CLASS}
    assert set(counts) == set(HERO_BY_CLASS)
    assert all(count >= 3 for count in counts.values())
    assert counts["fighter"] == 4
    assert sum(counts.values()) == 37
    assert len(COMBAT_BUILD_VARIANTS) == 37


def test_martial_build_matrix_preserves_role_variety() -> None:
    expected = {
        "fighter": {"great-weapon", "sword-shield", "archer", "dual-wield"},
        "barbarian": {"great-weapon", "weapon-shield", "dual-wield"},
        "monk": {"unarmed-offense", "weapon-monk", "defensive-mobile"},
        "paladin": {"great-weapon", "sword-shield", "support-healer"},
        "ranger": {"archer", "dual-wield", "sword-shield"},
        "rogue": {"duelist", "dual-wield", "ranged"},
    }
    for class_id, build_ids in expected.items():
        assert {variant.id for variant in combat_build_variants_for(class_id)} == build_ids


def test_caster_and_hybrid_build_matrix_preserves_distinct_combat_roles() -> None:
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


def test_every_build_reuses_its_single_class_progression_spine() -> None:
    for (class_id, build_id), variant in COMBAT_BUILD_VARIANTS.items():
        assert (variant.class_id, variant.id) == (class_id, build_id)
        assert variant.shared_progression_id == f"{class_id}-1-20"
        assert variant.status in {"active", "planned"}


def test_fighter_great_weapon_is_active_without_changing_public_build_identity() -> None:
    great_weapon = get_combat_build_variant("fighter", "great-weapon")
    assert great_weapon.status == "active"
    assert "Graze" in great_weapon.notes
    assert CANONICAL_BUILD_ID == "canonical"
    assert great_weapon.id != CANONICAL_BUILD_ID


def test_subclass_specific_builds_are_explicit_without_redefining_the_class() -> None:
    land = get_combat_build_variant("druid", "land-damage")
    moon = get_combat_build_variant("druid", "moon-melee")
    assert land.required_subclass_id == "circle-land"
    assert moon.required_subclass_id == "circle-moon"
    assert moon.status == "planned"
    assert "RAW audit" in moon.notes


def test_druid_compatibility_view_has_one_shared_source_of_truth() -> None:
    assert set(DRUID_COMBAT_BUILD_VARIANTS) == {"land-damage", "healer", "moon-melee"}
    for build_id, variant in DRUID_COMBAT_BUILD_VARIANTS.items():
        assert variant is get_combat_build_variant("druid", build_id)


def test_build_registry_does_not_change_public_certification_key() -> None:
    assert CANONICAL_BUILD_ID == "canonical"
    assert all(build_id != CANONICAL_BUILD_ID for _, build_id in COMBAT_BUILD_VARIANTS)
