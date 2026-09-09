from __future__ import annotations

import logging

from app.domain.grid import BattleMapDefinition, DeploymentZone

logger = logging.getLogger(__name__)


def build_standard_iron_pit_map() -> BattleMapDefinition:
    """Return the approved single Iron Pit VTT battlefield: 24 x 16 five-foot squares."""
    try:
        return BattleMapDefinition(
            id="iron-pit-standard-vtt",
            width_squares=24,
            height_squares=16,
            cell_size_ft=5,
        )
    except Exception:
        logger.exception("Failed to build the standard Iron Pit VTT map definition.")
        raise


def build_hero_deployment_zone() -> DeploymentZone:
    """Return the approved west-side 8 x 12 hero setup zone."""
    try:
        return DeploymentZone(
            x=0,
            y=2,
            width_squares=8,
            height_squares=12,
            front_edge="east",
        )
    except Exception:
        logger.exception("Failed to build the standard hero deployment zone.")
        raise


def build_monster_deployment_zone() -> DeploymentZone:
    """Return the approved east-side 8 x 12 monster setup zone."""
    try:
        return DeploymentZone(
            x=16,
            y=2,
            width_squares=8,
            height_squares=12,
            front_edge="west",
        )
    except Exception:
        logger.exception("Failed to build the standard monster deployment zone.")
        raise
