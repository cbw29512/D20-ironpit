from app.content.druid_combat_build_variants import DRUID_COMBAT_BUILD_VARIANTS
from app.content.druid_combat_levels import DRUID_COMBAT_LEVELS, druid_arena_ignored, druid_combat_features
from app.content.canonical_class_combat_spines import canonical_combat_features


def test_druid_combat_spine_is_complete_and_contiguous() -> None:
    assert tuple(DRUID_COMBAT_LEVELS) == tuple(range(1, 21))
    assert all(row.level == level for level, row in DRUID_COMBAT_LEVELS.items())
    assert all(len(row.spell_slots) == 9 for row in DRUID_COMBAT_LEVELS.values())


def test_druid_official_resource_and_slot_landmarks_are_locked() -> None:
    assert DRUID_COMBAT_LEVELS[1].wild_shape_uses == 0
    assert DRUID_COMBAT_LEVELS[2].wild_shape_uses == 2
    assert DRUID_COMBAT_LEVELS[6].wild_shape_uses == 3
    assert DRUID_COMBAT_LEVELS[17].wild_shape_uses == 4
    assert DRUID_COMBAT_LEVELS[1].spell_slots == (2, 0, 0, 0, 0, 0, 0, 0, 0)
    assert DRUID_COMBAT_LEVELS[5].spell_slots == (4, 3, 2, 0, 0, 0, 0, 0, 0)
    assert DRUID_COMBAT_LEVELS[17].spell_slots == (4, 3, 3, 3, 2, 1, 1, 1, 1)
    assert DRUID_COMBAT_LEVELS[20].spell_slots == (4, 3, 3, 3, 3, 2, 2, 1, 1)


def test_land_damage_features_accumulate_without_rebuilding_levels() -> None:
    level_ten = druid_combat_features(10)
    assert "druid-spellcasting" in level_ten
    assert {"land-arid-spells", "lands-aid", "natural-recovery", "natures-ward-fire"}.isdisjoint(level_ten)
    land_ten = canonical_combat_features("druid", 10, "circle-land")
    assert {"land-arid-spells", "lands-aid", "natural-recovery", "natures-ward-fire"} <= set(land_ten)


def test_noncombat_druid_features_stay_out_of_arena_runtime() -> None:
    ignored = druid_arena_ignored(20)
    assert "druidic" in ignored
    assert "speak-with-animals" in ignored
    assert "wild-companion" in ignored


def test_druid_role_variants_share_one_class_spine_and_do_not_overclaim_readiness() -> None:
    assert set(DRUID_COMBAT_BUILD_VARIANTS) == {"land-damage", "healer", "moon-melee"}
    variants = tuple(DRUID_COMBAT_BUILD_VARIANTS.values())
    assert {variant.shared_progression_id for variant in variants} == {"druid-1-20"}
    assert DRUID_COMBAT_BUILD_VARIANTS["land-damage"].status == "planned"
    assert DRUID_COMBAT_BUILD_VARIANTS["healer"].status == "planned"
    assert DRUID_COMBAT_BUILD_VARIANTS["healer"].subclass_id == "circle-sea"
    assert DRUID_COMBAT_BUILD_VARIANTS["moon-melee"].status == "planned"
    assert DRUID_COMBAT_BUILD_VARIANTS["moon-melee"].subclass_id == "circle-moon"
