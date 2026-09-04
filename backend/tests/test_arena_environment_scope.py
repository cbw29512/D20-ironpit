from app.content.arena_eligibility import source_environment_reason, standard_arena_eligible
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.catalog import CoverageStatus
from app.domain.movement import MovementModes


def test_source_speed_classification_matches_standard_arena_policy() -> None:
    assert source_environment_reason("5 ft., Swim 30 ft.") == "aquatic-only"
    assert source_environment_reason("0 ft., Swim 50 ft.") == "aquatic-only"
    assert source_environment_reason("10 ft., Swim 40 ft.") is None
    assert source_environment_reason("30 ft., Swim 40 ft.") is None
    assert source_environment_reason("0 ft., Fly 40 ft., Swim 40 ft.") is None


def test_swim_only_srd_monsters_are_deferred_from_standard_arena() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    aquatic_only = {
        "Giant Shark", "Hunter Shark", "Killer Whale", "Piranha", "Reef Shark", "Swarm of Piranhas",
    }
    for name in aquatic_only:
        card = cards[name]
        assert card.coverage_status is CoverageStatus.BLOCKED
        assert card.runnable_template_id is None
        assert card.blockers == ["deferred-environment:aquatic-only"]

    for name in {"Archelon", "Merrow", "Sahuagin Warrior"}:
        assert cards[name].blockers != ["deferred-environment:aquatic-only"]


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
