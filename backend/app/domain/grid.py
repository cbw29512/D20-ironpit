from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


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
    goal_reachable: bool


class GridDestinationPlan(BaseModel):
    """One legal destination reachable within a movement budget."""

    destination: GridPosition
    path: list[GridPosition] = Field(default_factory=list)
    movement_cost_ft: int = Field(default=0, ge=0)


class OffensiveMovementIntent(BaseModel):
    """Action-neutral target approach or exact tactical path."""

    mode: Literal["target", "path"] = "target"
    family: Literal["melee", "ranged", "spell", "ability"]
    target_id: str | None = None
    desired_distance_ft: int | None = Field(default=None, ge=0)
    path: list[GridPosition] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_mode(self) -> "OffensiveMovementIntent":
        if self.mode == "target":
            if not self.target_id or self.desired_distance_ft is None or self.path:
                raise ValueError("Target movement requires target/distance and no exact path.")
        elif self.target_id is not None or self.desired_distance_ft is not None or not self.path:
            raise ValueError("Path movement requires a non-empty path and no target/distance.")
        return self
