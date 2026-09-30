from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, DamageTypeName
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


class GridBarrierEdge(BaseModel):
    """One blocked 5-foot transition between two orthogonally adjacent grid cells."""

    first: GridPosition
    second: GridPosition

    @model_validator(mode="after")
    def validate_adjacent_cells(self) -> "GridBarrierEdge":
        try:
            distance = abs(self.first.x - self.second.x) + abs(self.first.y - self.second.y)
            if distance != 1:
                raise ValueError("Barrier edges must separate orthogonally adjacent grid cells.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Barrier edge validation failed.")
            raise RuntimeError("Barrier edge validation failed.") from exc

    def canonical_key(self) -> tuple[tuple[int, int], tuple[int, int]]:
        try:
            endpoints = sorted(((self.first.x, self.first.y), (self.second.x, self.second.y)))
            return endpoints[0], endpoints[1]
        except Exception as exc:
            logger.exception("Barrier edge key could not be resolved.")
            raise RuntimeError("Barrier edge key could not be resolved.") from exc


class PersistentBarrierAction(BaseModel):
    """Immutable parameters shared by spells/features that create destructible barriers."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    cast_range_ft: int = Field(ge=0)
    concentration: bool = False
    duration_rounds: int = Field(ge=1)
    permanent_after_full_duration: bool = False
    min_sections: int = Field(default=1, ge=1, le=100)
    max_sections: int = Field(ge=1, le=100)
    sections_must_be_contiguous: bool = False
    section_length_ft: int = Field(ge=5)
    section_height_ft: int = Field(ge=0)
    section_thickness_inches: int = Field(ge=1)
    armor_class: int = Field(ge=1, le=40)
    hit_points_per_section: int = Field(ge=1)
    damage_immunities: list[DamageTypeName] = Field(default_factory=list)
    blocks_movement: bool = True
    blocks_line_of_sight: bool = True
    material: str | None = None
    animation: str = "persistent-barrier"
    source: str | None = None

    @model_validator(mode="after")
    def validate_grid_dimensions(self) -> "PersistentBarrierAction":
        try:
            if self.min_sections > self.max_sections:
                raise ValueError("Barrier minimum sections cannot exceed maximum sections.")
            if self.section_length_ft % 5:
                raise ValueError("Barrier section length must use 5-foot grid increments.")
            if self.permanent_after_full_duration and not self.concentration:
                raise ValueError("Permanent-after-duration barriers require Concentration.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Persistent barrier action validation failed for %s.", self.id)
            raise RuntimeError("Persistent barrier action could not be validated.") from exc


class PersistentBarrierSectionState(BaseModel):
    """Mutable per-fight durability and occupied edges for one barrier section."""

    section_id: str = Field(min_length=1)
    edges: list[GridBarrierEdge] = Field(min_length=1)
    current_hp: int = Field(ge=0)
    armor_class: int = Field(ge=1, le=40)
    damage_immunities: list[DamageTypeName] = Field(default_factory=list)
    destroyed: bool = False


class PersistentBarrierState(BaseModel):
    """Fresh per-fight state for one placed persistent barrier source."""

    barrier_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_side: Literal["heroes", "monsters"]
    action_id: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    concentration: bool = False
    applied_round: int = Field(ge=1)
    expires_round: int = Field(ge=2)
    permanent_after_full_duration: bool = False
    blocks_movement: bool = True
    blocks_line_of_sight: bool = True
    sections: list[PersistentBarrierSectionState] = Field(min_length=1)
    animation: str = "persistent-barrier"
