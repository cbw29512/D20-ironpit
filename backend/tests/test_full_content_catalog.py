from collections import Counter

from app.content.capability_registry import load_capability_definitions
from app.content.catalog import build_full_content_catalog
from app.content.certified_heroes import build_certified_hero_registry
from app.content.monster_catalog import load_monster_rows
from app.domain.catalog import CoverageStatus


def test_catalog_contains_one_canonical_hero_for_every_class_level() -> None:
    catalog = build_full_content_catalog()
    assert catalog.hero_count == 240
    assert len(catalog.heroes) == 240
    assert len({card.id for card in catalog.heroes}) == 240

    counts = Counter(card.class_id for card in catalog.heroes)
    assert set(counts.values()) == {20}
    assert len(counts) == 12
    for class_id in counts:
        class_cards = [card for card in catalog.heroes if card.class_id == class_id]
        assert {card.level for card in class_cards} == set(range(1, 21))
        for level in range(1, 21):
            level_cards = [card for card in class_cards if card.level == level]
            assert len(level_cards) == 1
            assert {card.build_id for card in level_cards} == {"canonical"}


def test_catalog_contains_all_330_srd_5_2_1_monsters() -> None:
    catalog = build_full_content_catalog()
    assert catalog.monster_count == 330
    assert len(catalog.monsters) == 330
    assert len({monster.id for monster in catalog.monsters}) == 330
    assert len({monster.name for monster in catalog.monsters}) == 330
    assert all(monster.source_reference for monster in catalog.monsters)

    crab = next(monster for monster in catalog.monsters if monster.name == "Crab")
    crocodile = next(monster for monster in catalog.monsters if monster.name == "Crocodile")
    assert (crab.source_page, crab.challenge_rating) == (347, "0 (XP 10; PB +2)")
    assert crab.runnable_template_id == "srd-crab"
    assert crab.coverage_status is CoverageStatus.RAW_READY
    assert (crocodile.source_page, crocodile.challenge_rating) == (347, "1/2 (XP 100; PB +2)")
    assert crocodile.coverage_status is CoverageStatus.RAW_READY
    assert crocodile.runnable_template_id == "srd-crocodile"


def test_constrictor_snake_source_correction_removes_neighbor_bleed() -> None:
    row = next(row for row in load_monster_rows() if row["name"] == "Constrictor Snake")
    assert row["sourcePage"] == 346
    assert row["sourceReference"] == "SRD 5.2.1 p. 346"
    assert row["traits"] == ""
    assert "Crab Tiny Beast" not in str(row["actions"])
    assert "Crab Tiny Beast" not in str(row["rawText"])
    assert "Crocodile Large Beast" not in str(row["rawText"])


def test_uncertified_cards_fail_closed_in_catalog() -> None:
    catalog = build_full_content_catalog()
    barbarian_20 = next(
        card for card in catalog.heroes
        if card.class_id == "barbarian" and card.level == 20 and card.build_id == "canonical"
    )
    assert barbarian_20.coverage_status is CoverageStatus.BLOCKED
    assert barbarian_20.runnable_template_id is None
    assert barbarian_20.blockers

    commoner = next(monster for monster in catalog.monsters if monster.name == "Commoner")
    assert commoner.coverage_status is CoverageStatus.BLOCKED
    assert commoner.runnable_template_id is None
    assert "uncertified-trait:training" in commoner.blockers


def test_current_audited_heroes_are_raw_ready() -> None:
    catalog = build_full_content_catalog()
    ready_heroes = [card for card in catalog.heroes if card.coverage_status is CoverageStatus.RAW_READY]
    actual = {
        (card.class_id, card.level, card.build_id, card.name, card.runnable_template_id)
        for card in ready_heroes
    }
    expected = {
        (class_id, level, build_id, name, template_id)
        for (class_id, level, build_id), (name, template_id) in build_certified_hero_registry().items()
    }
    assert actual == expected
    assert all(not card.blockers for card in ready_heroes)


def test_current_certified_monsters_link_to_runtime_definitions() -> None:
    catalog = build_full_content_catalog()
    runtime_ids = set(load_capability_definitions())
    ready = [monster for monster in catalog.monsters if monster.coverage_status is CoverageStatus.RAW_READY]
    linked_ids = [monster.runnable_template_id for monster in ready]

    assert ready
    assert all(not monster.blockers for monster in ready)
    assert all(template_id in runtime_ids for template_id in linked_ids)
    assert len(linked_ids) == len(set(linked_ids))
