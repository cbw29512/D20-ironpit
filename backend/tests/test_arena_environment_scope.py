from app.content.arena_eligibility import standard_arena_eligible
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.catalog import CoverageStatus
from app.domain.movement import MovementModes


def test_aquatic_only_killer_whale_is_deferred_from_standard_arena() -> None:
    templates = build_legacy_monster_templates()
    assert all(template.name != "Killer Whale" for template in templates)

    card = next(card for card in build_monster_catalog() if card.name == "Killer Whale")
    assert card.coverage_status is CoverageStatus.BLOCKED
    assert card.runnable_template_id is None
    assert card.blockers == ["deferred-environment:aquatic-only"]


def test_standard_arena_eligibility_is_movement_driven() -> None:
    whale = next(template for template in build_zero_engine_monsters() if template.name == "Killer Whale")
    swimmer = whale.model_copy(update={
        "name": "Synthetic Swimmer",
        "movement_modes": MovementModes(walk_ft=0, swim_ft=40),
    })
    nominal_swimmer = whale.model_copy(update={
        "name": "Synthetic Nominal Swimmer",
        "movement_modes": MovementModes(walk_ft=5, swim_ft=40),
    })
    slow_land = whale.model_copy(update={
        "name": "Synthetic Slow Land Creature",
        "movement_modes": MovementModes(walk_ft=5),
    })
    flyer = swimmer.model_copy(update={
        "name": "Synthetic Flyer",
        "movement_modes": MovementModes(walk_ft=0, fly_ft=40, swim_ft=40),
    })
    assert standard_arena_eligible(swimmer) is False
    assert standard_arena_eligible(nominal_swimmer) is False
    assert standard_arena_eligible(slow_land) is True
    assert standard_arena_eligible(flyer) is True


def test_land_arena_grapple_batch_remains_eligible() -> None:
    names = {template.name for template in build_legacy_monster_templates()}
    assert {"Giant Scorpion", "Grick", "Griffon"} <= names
