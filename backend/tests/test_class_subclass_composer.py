from app.content.canonical_class_combat_spines import (
    CANONICAL_CLASS_COMBAT_SPINES,
    canonical_base_class_features,
    canonical_combat_features,
)
from app.content.hero_progressions import HERO_BY_CLASS
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


def test_every_canonical_subclass_is_a_sparse_overlay_on_its_base_class() -> None:
    assert set(SUBCLASS_COMBAT_OVERLAYS) == {hero.subclass_id for hero in HERO_BY_CLASS.values()}
    for subclass_id, overlay in SUBCLASS_COMBAT_OVERLAYS.items():
        assert overlay.class_id in HERO_BY_CLASS
        assert HERO_BY_CLASS[overlay.class_id].subclass_id == subclass_id
        assert all(1 <= level <= 20 for level in overlay.deltas)
        assert len(overlay.deltas) < 20


def test_base_plus_subclass_reproduces_every_researched_level_feature_set() -> None:
    for class_id in CANONICAL_CLASS_COMBAT_SPINES:
        for level in range(1, 21):
            legacy = _legacy_combined_features(class_id, level)
            composed = canonical_combat_features(class_id, level)
            assert len(composed) == len(set(composed)), (class_id, level)
            assert set(composed) == set(legacy), (class_id, level, composed, legacy)


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
