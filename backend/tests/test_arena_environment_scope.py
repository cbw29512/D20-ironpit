from app.content.arena_eligibility import deferred_environment_reason, standard_arena_eligible
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.content.simple_monster_source_definitions import build_simple_source_definitions
from app.domain.movement import MovementModes


def test_aquatic_only_killer_whale_is_not_environment_deferred() -> None:
    whale = next(template for template in build_zero_engine_monsters() if template.name == "Killer Whale")
    assert deferred_environment_reason(whale.movement_modes) is None
    assert standard_arena_eligible(whale) is True

    card = next(card for card in build_monster_catalog() if card.name == "Killer Whale")
    assert "deferred-environment:aquatic-only" not in card.blockers


def test_standard_arena_magically_supports_swim_only_creatures() -> None:
    whale = next(template for template in build_zero_engine_monsters() if template.name == "Killer Whale")
    swimmer = whale.model_copy(update={"name": "Synthetic Swimmer", "movement_modes": MovementModes(walk_ft=0, swim_ft=40)})
    land_swimmer = whale.model_copy(update={"name": "Synthetic Land Swimmer", "movement_modes": MovementModes(walk_ft=30, swim_ft=40)})
    slow_land = whale.model_copy(update={"name": "Synthetic Slow Land Creature", "movement_modes": MovementModes(walk_ft=5)})
    flyer = whale.model_copy(update={"name": "Synthetic Flyer", "movement_modes": MovementModes(walk_ft=0, fly_ft=40)})
    immobile = whale.model_copy(update={"name": "Synthetic MV0 Creature", "movement_modes": MovementModes(walk_ft=0)})

    assert deferred_environment_reason(swimmer.movement_modes) is None
    assert standard_arena_eligible(swimmer) is True
    assert standard_arena_eligible(land_swimmer) is True
    assert standard_arena_eligible(slow_land) is True
    assert standard_arena_eligible(flyer) is True
    assert standard_arena_eligible(immobile) is False


def test_srd_catalog_has_no_aquatic_environment_deferrals() -> None:
    deferred = {
        str(row["name"])
        for row in load_monster_rows()
        if deferred_environment_reason(row["speed"]) is not None
    }
    assert deferred == set()


def test_aquatic_simple_source_monsters_are_not_filtered_out() -> None:
    definitions = build_simple_source_definitions()
    names = {definition.name for definition in definitions.values()}
    assert {"Giant Shark", "Hunter Shark", "Piranha"} <= names


def test_land_arena_grapple_batch_remains_eligible() -> None:
    names = {template.name for template in build_legacy_monster_templates()}
    assert {"Giant Scorpion", "Grick", "Griffon"} <= names
