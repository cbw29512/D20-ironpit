"""Immutable source-turn damage targeting a live relationship, not a creature name."""
from __future__ import annotations

from typing import Literal
import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class SourceTurnRelationDamage(BaseModel):
    source_name: str = Field(min_length=1)
    target_relation: Literal["creatures_grappling_source", "creatures_grappled_by_source"]
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    damage_type: DamageType
    damage_bonus: int = Field(default=0, exclude_if=lambda value: value == 0)
    save_ability: str | None = Field(default=None, exclude_if=lambda value: value is None)
    save_dc: int | None = Field(default=None, ge=1, le=40, exclude_if=lambda value: value is None)

    @model_validator(mode="after")
    def require_complete_save(self) -> "SourceTurnRelationDamage":
        try:
            if (self.save_ability is None) != (self.save_dc is None):
                raise ValueError("Source-turn relation damage save requires ability and DC.")
            if self.save_ability is not None and self.save_ability not in {
                "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"
            }:
                raise ValueError("Unsupported source-turn relation save ability.")
            return self
        except Exception:
            logger.exception("Invalid source-turn relation damage definition.")
            raise
