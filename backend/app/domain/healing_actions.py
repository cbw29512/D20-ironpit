from __future__ import annotations

import logging
from pydantic import BaseModel, Field, model_validator
from app.domain.action_types import ActionCost, HealingTargetMode, ConditionName

logger = logging.getLogger(__name__)

class HealingAction(BaseModel):
    """A printed healing option with its actual action cost and target restrictions."""

    id: str
    name: str
    action_cost: ActionCost
    range_ft: int = Field(default=5, ge=0)
    target_mode: HealingTargetMode = "self_or_ally"
    max_targets: int = Field(default=1, ge=1, le=20)
    area_radius_ft: int | None = Field(default=None, ge=5)
    dice_count: int = Field(default=0, ge=0, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    healing_bonus: int = Field(default=0, ge=0)
    restore_to_effective_max: bool = False
    percentile_success_max: int | None = Field(default=None, ge=1, le=100)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=200)
    healing_from_resource_pool: bool = False
    excluded_creature_types: list[str] = Field(default_factory=list)
    removable_conditions: list[ConditionName] = Field(default_factory=list)
    prone_reaction_stand: bool = False
    secondary_target_within_ft: int | None = Field(default=None, ge=5)
    grants_temporary_hp: bool = False
    shared_healing_pool: int | None = Field(default=None, ge=1)
    stabilize_at_zero: bool = False
    animation: str = "healing"

    @model_validator(mode="after")
    def validate_linked_targets(self) -> "HealingAction":
        try:
            if self.secondary_target_within_ft is not None and self.max_targets < 2:
                raise ValueError("Linked secondary-target distance requires a multi-target healing action.")
            if self.healing_from_resource_pool and (
                self.resource_id is None or self.dice_count or self.restore_to_effective_max
                or self.max_targets != 1 or self.percentile_success_max is not None
            ):
                raise ValueError("Pool healing requires one target, a resource, and fixed healing.")
            if self.shared_healing_pool is not None and (
                self.max_targets < 2 or self.dice_count or self.restore_to_effective_max
                or self.healing_from_resource_pool or self.stabilize_at_zero
            ):
                raise ValueError("Shared healing pool requires multi-target fixed-pool healing.")
            if self.stabilize_at_zero and (
                self.dice_count or self.healing_bonus or self.restore_to_effective_max
                or self.shared_healing_pool or self.healing_from_resource_pool
            ):
                raise ValueError("Stabilize-only healing cannot also restore HP.")
            return self
        except Exception:
            logger.exception("Invalid healing action schema %s.", self.id)
            raise
