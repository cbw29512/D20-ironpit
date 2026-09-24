from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ActionCost, DamageTypeName
from app.domain.grid import GridPosition
from app.domain.size import CreatureSize


class PersistentHazardAction(BaseModel):
    """Immutable source parameters for a stationary battlefield hazard."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: int = Field(ge=0, le=9)
    action_cost: ActionCost = "action"
    cast_range_ft: int = Field(ge=0)
    duration_rounds: int = Field(ge=1)
    footprint_size: CreatureSize
    trigger_radius_ft: int = Field(ge=0)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    failure_damage: int = Field(ge=0)
    success_damage: int = Field(ge=0)
    damage_type: DamageTypeName
    max_total_damage: int = Field(ge=1)
    animation: str = "persistent-hazard"
    source: str | None = None


class PersistentHazardState(BaseModel):
    """Mutable per-fight state for one placed persistent hazard."""

    hazard_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_side: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    position: GridPosition
    footprint_size: CreatureSize
    trigger_radius_ft: int = Field(ge=0)
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    failure_damage: int = Field(ge=0)
    success_damage: int = Field(ge=0)
    damage_type: DamageTypeName
    remaining_damage_capacity: int = Field(ge=0)
    expires_round: int = Field(ge=1)
    triggered_turn_keys: dict[str, str] = Field(default_factory=dict)
    animation: str = "persistent-hazard"
