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


def test_catalog_contains_all_330_srd_5_2_1_monsters() -> None:
    catalog = build_full_content_catalog()
    assert catalog.monster_count == 330
    assert len(catalog.monsters) == 330
    assert len({monster.id for monster in catalog.monsters}) == 330
    assert len({monster.name for monster in catalog.monsters}) == 330
    assert all(monster.source_reference for monster in catalog.monsters)

    crab = next(monster for monster in catalog.monsters if monster.name == "Crab")
    crocodile = next(monster for monster in catalog.monsters if monster.name == "Crocodile")
    assert (crab.source_page, crab.challenge_rating) == (346, "0 (XP 10; PB +2)")
    assert crab.runnable_template_id == "srd-crab"
    assert crab.coverage_status is CoverageStatus.RAW_READY
    assert (crocodile.source_page, crocodile.challenge_rating) == (346, "1/2 (XP 100; PB +2)")
    assert crocodile.coverage_status is CoverageStatus.RAW_READY
    assert crocodile.runnable_template_id == "srd-crocodile"


def test_uncertified_cards_fail_closed_in_catalog() -> None:
    catalog = build_full_content_catalog()
    barbarian_20 = next(
        card for card in catalog.heroes
        if card.class_id == "barbarian" and card.level == 20 and card.build_id == "great-weapon"
    )
    assert barbarian_20.coverage_status is CoverageStatus.BLOCKED
    assert barbarian_20.runnable_template_id is None
    assert barbarian_20.blockers

    blocked_monster = next(monster for monster in catalog.monsters if monster.coverage_status is CoverageStatus.BLOCKED)
    assert blocked_monster.runnable_template_id is None
    assert blocked_monster.blockers


def test_current_audited_heroes_are_raw_ready() -> None:
    catalog = build_full_content_catalog()
    ready_heroes = [card for card in catalog.heroes if card.coverage_status is CoverageStatus.RAW_READY]
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
        for monster in catalog.monsters if monster.coverage_status is CoverageStatus.RAW_READY
    }
    assert len(ready_monsters) == 59
    assert ready_monsters == {
        "Awakened Shrub": "srd-awakened-shrub",
        "Axe Beak": "srd-axe-beak",
        "Baboon": "srd-baboon",
        "Badger": "srd-badger",
        "Bandit": "srd-bandit",
        "Bat": "srd-bat",
        "Black Bear": "srd-black-bear",
        "Boar": "srd-boar",
        "Brown Bear": "srd-brown-bear",
        "Camel": "srd-camel",
        "Cat": "srd-cat",
        "Commoner": "srd-commoner",
        "Constrictor Snake": "srd-constrictor-snake",
        "Crab": "srd-crab",
        "Crocodile": "srd-crocodile",
        "Deer": "srd-deer",
        "Dire Wolf": "srd-dire-wolf",
        "Draft Horse": "srd-draft-horse",
        "Eagle": "srd-eagle",
        "Elk": "srd-elk",
        "Frog": "srd-frog",
        "Giant Badger": "srd-giant-badger",
        "Giant Bat": "srd-giant-bat",
        "Giant Boar": "srd-giant-boar",
        "Giant Centipede": "srd-giant-centipede",
        "Giant Crab": "srd-giant-crab",
        "Giant Fire Beetle": "srd-giant-fire-beetle",
        "Giant Goat": "srd-giant-goat",
        "Giant Lizard": "srd-giant-lizard",
        "Giant Owl": "srd-giant-owl",
        "Giant Rat": "srd-giant-rat",
        "Giant Weasel": "srd-giant-weasel",
        "Goblin Warrior": "srd-goblin-warrior",
        "Guard": "srd-guard",
        "Hawk": "srd-hawk",
        "Hyena": "srd-hyena",
        "Lizard": "srd-lizard",
        "Mastiff": "srd-mastiff",
        "Mule": "srd-mule",
        "Ogre": "srd-ogre",
        "Owl": "srd-owl",
        "Owlbear": "srd-owlbear",
        "Panther": "srd-panther",
        "Plesiosaurus": "srd-plesiosaurus",
        "Polar Bear": "srd-polar-bear",
        "Pony": "srd-pony",
        "Pteranodon": "srd-pteranodon",
        "Rat": "srd-rat",
        "Raven": "srd-raven",
        "Rhinoceros": "srd-rhinoceros",
        "Riding Horse": "srd-riding-horse",
        "Saber-Toothed Tiger": "srd-saber-toothed-tiger",
        "Scout": "srd-scout",
        "Tiger": "srd-tiger",
        "Vulture": "srd-vulture",
        "Warhorse": "srd-warhorse",
        "Warrior Infantry": "srd-warrior-infantry",
        "Weasel": "srd-weasel",
        "Wolf": "srd-wolf",
    }
