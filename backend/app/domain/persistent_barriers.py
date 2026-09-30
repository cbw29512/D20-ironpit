from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, DamageTypeName
from app.domain.grid import GridPosition


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
            raise RuntimeError("Barrier edge validation failed.") from exc

    def canonical_key(self) -> tuple[tuple[int, int], tuple[int, int]]:
        try:
            endpoints = sorted(((self.first.x, self.first.y), (self.second.x, self.second.y)))
            return endpoints[0], endpoints[1]
        except Exception as exc:
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
    max_sections: int = Field(ge=1, le=100)
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
    blocks_movement: bool = True
    blocks_line_of_sight: bool = True
    sections: list[PersistentBarrierSectionState] = Field(min_length=1)
    animation: str = "persistent-barrier"
