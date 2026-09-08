from app.content.arena_eligibility import deferred_environment_reason, standard_arena_eligible
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.catalog import CoverageStatus
from app.domain.movement import MovementModes


def test_hospitable_pit_promotes_killer_whale_without_environment_blocker() -> None:
    templates = build_legacy_monster_templates()
    whale = next(template for template in templates if template.name == "Killer Whale")
    assert whale.movement_modes.walk_ft == 5
    assert whale.movement_modes.swim_ft == 60
    assert whale.source_trait_names == ["Hold Breath"]
    assert deferred_environment_reason("Killer Whale") is None

    card = next(card for card in build_monster_catalog() if card.name == "Killer Whale")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-killer-whale"
    assert card.blockers == []


def test_magical_hospitality_never_rewrites_or_rejects_movement_modes() -> None:
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
    for template in (swimmer, nominal_swimmer, slow_land, flyer):
        assert standard_arena_eligible(template) is True

    assert swimmer.movement_modes == MovementModes(walk_ft=0, swim_ft=40)
    assert nominal_swimmer.movement_modes == MovementModes(walk_ft=5, swim_ft=40)
    assert flyer.movement_modes == MovementModes(walk_ft=0, fly_ft=40, swim_ft=40)


def test_existing_grapple_batch_remains_eligible() -> None:
    names = {template.name for template in build_legacy_monster_templates()}
    assert {"Giant Scorpion", "Grick", "Griffon"} <= names
