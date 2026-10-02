from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)

TacticalEffect = Literal["dash", "disengage", "dodge"]
TacticalUsePolicy = Literal["enable-offense", "defensive-fallback", "manual"]


class BonusActionTacticalGrant(BaseModel):
    """Declarative Bonus Action that composes standard tactical actions."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    effects: list[TacticalEffect] = Field(min_length=1, max_length=3)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    priority: int = Field(default=100, ge=0, le=1000)
    use_policy: TacticalUsePolicy = "manual"
    jump_distance_multiplier: int = Field(default=1, ge=1, le=4)
    temporary_hp_dice_count: int = Field(default=0, ge=0, le=20)
    temporary_hp_dice_size: int = Field(default=0, ge=0, le=100)

    @model_validator(mode="after")
    def validate_effects(self) -> "BonusActionTacticalGrant":
        try:
            if len(set(self.effects)) != len(self.effects):
                raise ValueError("Bonus tactical grant effects must be unique.")
            if self.use_policy == "enable-offense" and "dash" not in self.effects:
                raise ValueError("Enable-offense tactical grants must include Dash.")
            if self.use_policy == "defensive-fallback" and "dodge" not in self.effects:
                raise ValueError("Defensive tactical grants must include Dodge.")
            has_temp_hp = self.temporary_hp_dice_count > 0 or self.temporary_hp_dice_size > 0
            if has_temp_hp and not (self.temporary_hp_dice_count > 0 and self.temporary_hp_dice_size >= 2):
                raise ValueError("Temporary HP dice require both a positive count and a die size of at least 2.")
            return self
        except ValueError:
            logger.exception("Invalid Bonus Action tactical grant %s.", self.id)
            raise
        except Exception as exc:
            logger.exception("Failed to validate Bonus Action tactical grant %s.", self.id)
            raise RuntimeError("Bonus Action tactical grant validation failed.") from exc
