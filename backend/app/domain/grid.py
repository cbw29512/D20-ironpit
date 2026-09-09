from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GridPosition(BaseModel):
    """Top-left occupied cell for a combatant footprint on the Iron Pit grid."""

    x: int = Field(ge=0)
    y: int = Field(ge=0)


class BattleMapDefinition(BaseModel):
    """Immutable tactical-map dimensions shared by every combat resolver."""

    id: str = Field(min_length=1)
    width_squares: int = Field(ge=1)
    height_squares: int = Field(ge=1)
    cell_size_ft: Literal[5] = 5


class DeploymentZone(BaseModel):
    """Rectangular legal starting area with an explicit enemy-facing edge."""

    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width_squares: int = Field(ge=1)
    height_squares: int = Field(ge=1)
    front_edge: Literal["west", "east"]


class GridPlacementAssignment(BaseModel):
    """One deterministic starting-position assignment for a combatant."""

    combatant_id: str = Field(min_length=1)
    position: GridPosition


class GridMovementPlan(BaseModel):
    """Deterministic path proposal produced by the universal grid movement planner."""

    path: list[GridPosition] = Field(default_factory=list)
    movement_cost_ft: int = Field(default=0, ge=0)
    final_distance_ft: int = Field(ge=0)


class OffensiveMovementIntent(BaseModel):
    """Action-neutral reason for approaching an enemy through the shared movement engine."""

    target_id: str = Field(min_length=1)
    desired_distance_ft: int = Field(ge=0)
    family: Literal["melee", "ranged", "spell", "ability"]
