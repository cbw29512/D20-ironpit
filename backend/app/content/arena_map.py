from __future__ import annotations

import logging

from app.domain.grid import BattleMapDefinition, DeploymentZone

logger = logging.getLogger(__name__)


def build_standard_iron_pit_map() -> BattleMapDefinition:
    """Return the approved open Iron Pit combat battlefield: 24 x 16 five-foot squares."""
    try:
        return BattleMapDefinition(
            id="iron-pit-standard-vtt",
            width_squares=24,
            height_squares=16,
            cell_size_ft=5,
            support_materials=["stone"],
        )
    except Exception:
        logger.exception("Failed to build the standard Iron Pit VTT map definition.")
        raise


def build_hero_deployment_zone() -> DeploymentZone:
    """Return the west-side 2 x 3 starting formation."""
    try:
        return DeploymentZone(
            x=8,
            y=6,
            width_squares=2,
            height_squares=3,
            front_edge="east",
        )
    except Exception:
        logger.exception("Failed to build the standard hero deployment zone.")
        raise


def build_monster_deployment_zone() -> DeploymentZone:
    """Return the east-side 2 x 3 starting formation."""
    try:
        return DeploymentZone(
            x=14,
            y=6,
            width_squares=2,
            height_squares=3,
            front_edge="west",
        )
    except Exception:
        logger.exception("Failed to build the standard monster deployment zone.")
        raise
