from app.content.canonical_class_combat_spines import (
    CANONICAL_CLASS_COMBAT_SPINES,
    canonical_base_class_features,
    canonical_combat_features,
)
from app.content.barbarian_subclass_overlay_data import BARBARIAN_SUBCLASS_DELTA_DATA
from app.content.core_subclass_overlay_data import CORE_SUBCLASS_DELTA_DATA
from app.content.fighter_subclass_overlay_data import FIGHTER_SUBCLASS_DELTA_DATA
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.hero_variant_policy import TARGET_SUBCLASSES
from app.content.monk_subclass_overlay_data import MONK_SUBCLASS_DELTA_DATA
from app.content.paladin_subclass_overlay_data import PALADIN_SUBCLASS_DELTA_DATA
from app.content.ranger_subclass_overlay_data import RANGER_SUBCLASS_DELTA_DATA
from app.content.rogue_subclass_overlay_data import ROGUE_SUBCLASS_DELTA_DATA
from app.content.sorcerer_subclass_overlay_data import SORCERER_SUBCLASS_DELTA_DATA
from app.content.wizard_subclass_overlay_data import WIZARD_SUBCLASS_DELTA_DATA
from app.content.warlock_subclass_overlay_data import WARLOCK_SUBCLASS_DELTA_DATA
from app.content.subclass_combat_overlays import SUBCLASS_COMBAT_OVERLAYS, subclass_combat_features


def _legacy_combined_features(class_id: str, level: int) -> tuple[str, ...]:
    active: list[str] = []
    spine = CANONICAL_CLASS_COMBAT_SPINES[class_id]
    for current in range(1, level + 1):
        row = spine[current]
        removed = tuple(getattr(row, "features_removed", ()))
        added = tuple(getattr(row, "features_added", ()))
        active = [feature for feature in active if feature not in removed]
        active.extend(feature for feature in added if feature not in active)
    return tuple(active)


def test_subclass_registry_is_derived_from_authoritative_overlay_data() -> None:
    expected = (
        set(BARBARIAN_SUBCLASS_DELTA_DATA)
        | set(CORE_SUBCLASS_DELTA_DATA)
        | set(FIGHTER_SUBCLASS_DELTA_DATA)
        | set(MONK_SUBCLASS_DELTA_DATA)
        | set(PALADIN_SUBCLASS_DELTA_DATA)
        | set(RANGER_SUBCLASS_DELTA_DATA)
        | set(ROGUE_SUBCLASS_DELTA_DATA)
        | set(SORCERER_SUBCLASS_DELTA_DATA)
        | set(WIZARD_SUBCLASS_DELTA_DATA)
        | set(WARLOCK_SUBCLASS_DELTA_DATA)
    )
    assert set(SUBCLASS_COMBAT_OVERLAYS) == expected


def test_every_selected_canonical_subclass_is_registered_on_its_base_class() -> None:
    for class_id, hero in HERO_BY_CLASS.items():
        overlay = SUBCLASS_COMBAT_OVERLAYS[hero.subclass_id]
        assert overlay.class_id == class_id


def test_every_registered_subclass_is_a_sparse_overlay_in_its_target_family() -> None:
    for subclass_id, overlay in SUBCLASS_COMBAT_OVERLAYS.items():
        assert overlay.class_id in HERO_BY_CLASS
        assert overlay.subclass_id == subclass_id
        assert subclass_id in TARGET_SUBCLASSES[overlay.class_id]
        assert all(1 <= level <= 20 for level in overlay.deltas)
        assert len(overlay.deltas) < 20


def test_base_plus_selected_subclass_preserves_every_researched_feature_set() -> None:
    for class_id in CANONICAL_CLASS_COMBAT_SPINES:
        for level in range(1, 21):
            expected = set(_legacy_combined_features(class_id, level))
            expected.update(subclass_combat_features(HERO_BY_CLASS[class_id].subclass_id, level))
            composed = canonical_combat_features(class_id, level)
            assert len(composed) == len(set(composed)), (class_id, level)
            assert set(composed) == expected, (class_id, level, composed, expected)


def test_monk_base_spine_contains_no_open_hand_subclass_features() -> None:
    subclass_features = {
        feature
        for level in range(1, 21)
        for feature in subclass_combat_features("warrior-open-hand", level)
    }
    assert subclass_features
    assert subclass_features.isdisjoint(canonical_base_class_features("monk", 20))


def test_paladin_base_spine_contains_no_devotion_subclass_features() -> None:
    subclass_features = {
        feature
        for level in range(1, 21)
        for feature in subclass_combat_features("oath-devotion", level)
    }
    assert subclass_features
    assert subclass_features.isdisjoint(canonical_base_class_features("paladin", 20))


def test_ranger_base_spine_contains_no_hunter_subclass_features() -> None:
    subclass_features = {
        feature
        for level in range(1, 21)
        for feature in subclass_combat_features("hunter", level)
    }
    assert subclass_features
    assert subclass_features.isdisjoint(canonical_base_class_features("ranger", 20))


def test_wizard_base_spine_contains_no_evoker_subclass_features() -> None:
    subclass_features = {
        feature
        for level in range(1, 21)
        for feature in subclass_combat_features("evoker", level)
    }
    assert subclass_features
    assert subclass_features.isdisjoint(canonical_base_class_features("wizard", 20))


def test_sorcerer_base_spine_contains_no_draconic_subclass_features() -> None:
    subclass_features = {
        feature
        for level in range(1, 21)
        for feature in subclass_combat_features("draconic-sorcery", level)
    }
    assert subclass_features
    assert subclass_features.isdisjoint(canonical_base_class_features("sorcerer", 20))


def test_warlock_base_spine_contains_no_fiend_subclass_features() -> None:
    subclass_features = {
        feature
        for level in range(1, 21)
        for feature in subclass_combat_features("fiend-patron", level)
    }
    assert subclass_features
    assert subclass_features.isdisjoint(canonical_base_class_features("warlock", 20))


def test_fighter_base_never_gets_champion_features_without_champion_overlay() -> None:
    base_three = canonical_base_class_features("fighter", 3)
    champion_three = canonical_combat_features("fighter", 3, "champion")
    assert "improved-critical" not in base_three
    assert "remarkable-athlete" not in base_three
    assert "improved-critical" in champion_three
    assert "remarkable-athlete" in champion_three
    assert "action-surge" in base_three
    assert "tactical-mind" in base_three


def test_rogue_base_and_thief_overlay_are_independent() -> None:
    base_three = canonical_base_class_features("rogue", 3)
    thief_three = canonical_combat_features("rogue", 3, "thief")
    assert "sneak-attack" in base_three
    assert "cunning-action" in base_three
    assert "steady-aim" in base_three
    assert "thief-fast-hands" not in base_three
    assert "thief-fast-hands" in thief_three


def test_rogue_base_spine_contains_no_thief_subclass_features() -> None:
    subclass_features = {
        feature
        for level in range(1, 21)
        for feature in subclass_combat_features("thief", level)
    }
    assert subclass_features
    assert subclass_features.isdisjoint(canonical_base_class_features("rogue", 20))


def test_druid_base_is_shared_before_land_or_future_moon_builds() -> None:
    base_three = canonical_base_class_features("druid", 3)
    land_three = canonical_combat_features("druid", 3, "circle-land")
    assert "druid-spellcasting" in base_three
    assert "wild-shape" in base_three
    assert "lands-aid" not in base_three
    assert "land-arid-spells" not in base_three
    assert "lands-aid" in land_three
    assert "land-arid-spells" in land_three


def test_subclass_feature_accumulator_respects_feature_replacement() -> None:
    fighter_fifteen = subclass_combat_features("champion", 15)
    assert "improved-critical" not in fighter_fifteen
    assert "superior-critical" in fighter_fifteen
