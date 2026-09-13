from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.size import CreatureSize
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
SwallowCondition = Literal["blinded", "restrained"]
SwallowActionCost = Literal["action", "bonus_action"]


class SwallowAction(BaseModel):
    """Immutable source rule for a creature swallowing eligible targets."""

    id: str
    name: str = "Swallow"
    max_target_size: CreatureSize
    action_cost: SwallowActionCost = "action"
    max_swallowed_targets: int = Field(default=1, ge=1, le=20)
    requires_grappled_target: bool = True
    damage_dice_count: int = Field(ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.ACID
    first_tick_delay_rounds: int = Field(default=0, ge=0, le=20)
    tick_timing: Literal["source_turn_end"] = "source_turn_end"
    disgorge_after_first_tick: bool = False
    applies_blinded: bool = True
    applies_restrained: bool = True
    total_cover_from_outside: bool = True
    forbidden_attack_ids_while_active: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_damage(self) -> "SwallowAction":
        try:
            if self.damage_dice_count == 0 and self.damage_bonus <= 0:
                raise ValueError("Swallow ongoing damage must be positive.")
            return self
        except ValueError:
            raise
        except Exception:
            logger.exception("Failed to validate Swallow action %s.", self.id)
            raise


class SwallowedState(BaseModel):
    """Mutable encounter outcome; immutable damage rules remain on the source template."""

    source_id: str
    action_id: str
    applied_round: int = Field(ge=1)
    first_tick_round: int = Field(ge=1)
    applied_condition_ids: list[SwallowCondition] = Field(default_factory=list)
    total_cover_from_outside: bool = True

    @model_validator(mode="after")
    def validate_timing(self) -> "SwallowedState":
        try:
            if self.first_tick_round < self.applied_round:
                raise ValueError("Swallow first tick cannot precede application.")
            if len(set(self.applied_condition_ids)) != len(self.applied_condition_ids):
                raise ValueError("Swallow conditions cannot contain duplicates.")
            return self
        except ValueError:
            raise
        except Exception:
            logger.exception("Failed to validate swallowed runtime state.")
            raise
