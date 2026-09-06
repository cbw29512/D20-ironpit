from app.content.arena_eligibility import deferred_environment_reason, standard_arena_eligible
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.movement import MovementModes


def test_aquatic_only_killer_whale_is_not_blocked_by_movement() -> None:
    templates = build_legacy_monster_templates()
    assert any(template.name == "Killer Whale" for template in templates)

    card = next(card for card in build_monster_catalog() if card.name == "Killer Whale")
    assert not any(blocker.startswith("deferred-environment:") for blocker in card.blockers)


def test_standard_arena_eligibility_ignores_movement_modes() -> None:
    whale = next(template for template in build_zero_engine_monsters() if template.name == "Killer Whale")
    samples = [
        whale.model_copy(update={"name": "Synthetic Swimmer", "movement_modes": MovementModes(walk_ft=0, swim_ft=40)}),
        whale.model_copy(update={"name": "Synthetic Land Swimmer", "movement_modes": MovementModes(walk_ft=30, swim_ft=40)}),
        whale.model_copy(update={"name": "Synthetic Slow Land Creature", "movement_modes": MovementModes(walk_ft=5)}),
        whale.model_copy(update={"name": "Synthetic Flyer", "movement_modes": MovementModes(walk_ft=0, fly_ft=40)}),
        whale.model_copy(update={"name": "Synthetic MV0 Creature", "movement_modes": MovementModes(walk_ft=0)}),
    ]

    for template in samples:
        assert deferred_environment_reason(template.movement_modes) is None
        assert standard_arena_eligible(template) is True


def test_srd_catalog_has_no_movement_only_environment_deferrals() -> None:
    deferred = {
        str(row["name"])
        for row in load_monster_rows()
        if deferred_environment_reason(row["speed"]) is not None
    }

    assert deferred == set()


def test_existing_land_arena_batch_remains_eligible() -> None:
    names = {template.name for template in build_legacy_monster_templates()}
    assert {"Giant Scorpion", "Grick", "Griffon"} <= names
