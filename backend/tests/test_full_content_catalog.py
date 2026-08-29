from collections import Counter

from app.content.catalog import build_full_content_catalog
from app.domain.catalog import CoverageStatus


def test_catalog_contains_three_builds_for_every_core_class_level() -> None:
    catalog = build_full_content_catalog()
    assert catalog.hero_count == 720
    assert len(catalog.heroes) == 720
    assert len({card.id for card in catalog.heroes}) == 720

    counts = Counter(card.class_id for card in catalog.heroes)
    assert set(counts.values()) == {60}
    assert len(counts) == 12
    for class_id in counts:
        class_cards = [card for card in catalog.heroes if card.class_id == class_id]
        assert {card.level for card in class_cards} == set(range(1, 21))
        for level in range(1, 21):
            level_cards = [card for card in class_cards if card.level == level]
            assert len(level_cards) == 3
            assert len({card.build_id for card in level_cards}) == 3


def test_catalog_contains_all_srd_5_2_1_monsters() -> None:
    catalog = build_full_content_catalog()
    assert catalog.monster_count == 328
    assert len(catalog.monsters) == 328
    assert len({monster.id for monster in catalog.monsters}) == 328
    assert all(monster.source_reference for monster in catalog.monsters)


def test_uncertified_cards_fail_closed_in_catalog() -> None:
    catalog = build_full_content_catalog()
    barbarian_20 = next(
        card
        for card in catalog.heroes
        if card.class_id == "barbarian" and card.level == 20 and card.build_id == "great-weapon"
    )
    assert barbarian_20.coverage_status is CoverageStatus.BLOCKED
    assert barbarian_20.runnable_template_id is None
    assert barbarian_20.blockers

    blocked_monster = next(
        monster for monster in catalog.monsters if monster.coverage_status is CoverageStatus.BLOCKED
    )
    assert blocked_monster.runnable_template_id is None
    assert blocked_monster.blockers


def test_current_audited_heroes_are_raw_ready() -> None:
    catalog = build_full_content_catalog()
    ready_heroes = [
        card for card in catalog.heroes if card.coverage_status is CoverageStatus.RAW_READY
    ]

    assert {
        (card.class_id, card.level, card.build_id, card.name, card.runnable_template_id)
        for card in ready_heroes
    } == {
        ("barbarian", 1, "great-weapon", "Rokhan Stonefury", "rokhan-stonefury-l1"),
        ("fighter", 1, "great-weapon", "Karnok Stoneward", "karnok-stoneward-l1"),
    }
    assert all(not card.blockers for card in ready_heroes)


def test_current_certified_monsters_are_linked_to_runtime_templates() -> None:
    catalog = build_full_content_catalog()
    ready_monsters = {
        monster.name: monster.runnable_template_id
        for monster in catalog.monsters
        if monster.coverage_status is CoverageStatus.RAW_READY
    }
    assert ready_monsters == {
        "Axe Beak": "srd-axe-beak",
        "Bandit": "srd-bandit",
        "Black Bear": "srd-black-bear",
        "Brown Bear": "srd-brown-bear",
        "Camel": "srd-camel",
        "Commoner": "srd-commoner",
        "Deer": "srd-deer",
        "Dire Wolf": "srd-dire-wolf",
        "Draft Horse": "srd-draft-horse",
        "Giant Badger": "srd-giant-badger",
        "Giant Lizard": "srd-giant-lizard",
        "Giant Rat": "srd-giant-rat",
        "Giant Weasel": "srd-giant-weasel",
        "Goblin Warrior": "srd-goblin-warrior",
        "Guard": "srd-guard",
        "Wolf": "srd-wolf",
    }
