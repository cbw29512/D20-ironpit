from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName, ActionCost, DamageTypeName
from app.domain.grid import GridPosition


class PersistentBeneficialZoneAction(BaseModel):
    """Immutable source data for a placed beneficial battlefield zone."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    action_cost: ActionCost = "action"
    resource_id: str | None = None
    resource_cost: int = Field(default=0, ge=0)
    cast_range_ft: int = Field(ge=0)
    duration_rounds: int = Field(ge=1)
    shape: str = "cube"
    length_ft: int = Field(ge=5)
    move_action_cost: ActionCost | None = None
    move_distance_ft: int = Field(default=0, ge=0)
    move_range_ft: int = Field(default=0, ge=0)
    armor_class_bonus: int = 0
    cover_bonus: int = Field(default=0, ge=0, le=5)
    saving_throw_bonus: int = 0
    saving_throw_abilities: list[AbilityName] = Field(default_factory=list)
    ally_damage_resistances: list[DamageTypeName] = Field(default_factory=list)
    include_source_for_defense: bool = True
    end_if_source_incapacitated: bool = False
    end_if_source_dead: bool = False
    animation: str = "persistent-beneficial-zone"
    source: str | None = None


class PersistentBeneficialZoneState(BaseModel):
    """Fresh per-fight placement and lifetime for one beneficial zone."""

    zone_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_side: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    position: GridPosition
    applied_round: int = Field(ge=1)
    expires_round: int = Field(ge=2)
    length_ft: int = Field(ge=5)
    armor_class_bonus: int = 0
    cover_bonus: int = Field(default=0, ge=0, le=5)
    saving_throw_bonus: int = 0
    saving_throw_abilities: list[AbilityName] = Field(default_factory=list)
    ally_damage_resistances: list[DamageTypeName] = Field(default_factory=list)
    include_source_for_defense: bool = True
    end_if_source_incapacitated: bool = False
    end_if_source_dead: bool = False
    animation: str = "persistent-beneficial-zone"
