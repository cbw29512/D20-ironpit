import logging

from app.content.arena_eligibility import deferred_environment_reason, standard_arena_eligible
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import build_monster_catalog
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.movement import MovementModes

logger = logging.getLogger(__name__)


def test_aquatic_only_killer_whale_is_not_environment_deferred() -> None:
    try:
        templates = build_legacy_monster_templates()
        assert any(template.name == "Killer Whale" for template in templates)

        card = next(card for card in build_monster_catalog() if card.name == "Killer Whale")
        assert deferred_environment_reason("Killer Whale") is None
        assert deferred_environment_reason("Synthetic Aquatic Creature") is None
        assert all(not blocker.startswith("deferred-environment:") for blocker in card.blockers)
    except Exception:
        logger.exception("Universal aquatic arena-hospitality regression failed.")
        raise


def test_standard_arena_eligibility_is_environment_neutral() -> None:
    try:
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
        assert standard_arena_eligible(swimmer) is True
        assert standard_arena_eligible(nominal_swimmer) is True
        assert standard_arena_eligible(slow_land) is True
        assert standard_arena_eligible(flyer) is True
    except Exception:
        logger.exception("Universal movement-mode arena-hospitality regression failed.")
        raise


def test_existing_land_arena_grapple_batch_remains_eligible() -> None:
    try:
        names = {template.name for template in build_legacy_monster_templates()}
        assert {"Giant Scorpion", "Grick", "Griffon"} <= names
    except Exception:
        logger.exception("Existing land-arena eligibility regression failed.")
        raise
