from collections import Counter

from app.content.hero_catalog import build_hero_catalog
from app.content.hero_progressions import CANONICAL_BUILD_ID, CANONICAL_HEROES
from app.domain.catalog import CoverageStatus


def test_canonical_hero_roster_has_one_unique_name_per_core_class() -> None:
    assert len(CANONICAL_HEROES) == 12
    assert len({hero.class_id for hero in CANONICAL_HEROES}) == 12
    assert len({hero.hero_name for hero in CANONICAL_HEROES}) == 12


def test_each_canonical_hero_has_twenty_level_snapshots() -> None:
    cards = build_hero_catalog()
    assert len(cards) == 240
    assert set(Counter(card.class_id for card in cards).values()) == {20}
    for hero in CANONICAL_HEROES:
        levels = [card for card in cards if card.class_id == hero.class_id]
        assert {card.level for card in levels} == set(range(1, 21))
        assert {card.name for card in levels} == {hero.hero_name}
        assert {card.build_id for card in levels} == {CANONICAL_BUILD_ID}


def test_subclass_identity_appears_at_level_three() -> None:
    cards = build_hero_catalog()
    for hero in CANONICAL_HEROES:
        level_two = next(card for card in cards if card.class_id == hero.class_id and card.level == 2)
        level_three = next(card for card in cards if card.class_id == hero.class_id and card.level == 3)
        assert level_two.subclass_id is None
        assert level_three.subclass_id == hero.subclass_id
        assert level_three.subclass_name == hero.subclass_name


def test_only_certified_canonical_levels_are_runnable() -> None:
    ready = [card for card in build_hero_catalog() if card.coverage_status is CoverageStatus.RAW_READY]
    assert {(card.name, card.level, card.runnable_template_id) for card in ready} == {
        ("Karnok Stoneward", 1, "karnok-stoneward-l1"),
        ("Karnok Stoneward", 2, "karnok-stoneward-l2"),
        ("Karnok Stoneward", 3, "karnok-stoneward-l3"),
        ("Karnok Stoneward", 4, "karnok-stoneward-l4"),
        ("Karnok Stoneward", 5, "karnok-stoneward-l5"),
        ("Rokhan Stonefury", 1, "rokhan-stonefury-l1"),
        ("Rokhan Stonefury", 2, "rokhan-stonefury-l2"),
        ("Rokhan Stonefury", 3, "rokhan-stonefury-l3"),
        ("Rokhan Stonefury", 4, "rokhan-stonefury-l4"),
        ("Rokhan Stonefury", 5, "rokhan-stonefury-l5"),
        ("Rokhan Stonefury", 6, "rokhan-stonefury-l6"),
        ("Seraphine Dawnshield", 1, "seraphine-dawnshield-l1"),
        ("Seraphine Dawnshield", 2, "seraphine-dawnshield-l2"),
        ("Seraphine Dawnshield", 3, "seraphine-dawnshield-l3"),
        ("Seraphine Dawnshield", 4, "seraphine-dawnshield-l4"),
    }
