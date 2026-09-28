from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class SpellSpecificCastGrant(BaseModel):
    """Grant one named spell a slot-free cast path without changing other spells of that level."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    spell_id: str = Field(min_length=1)
    slot_level: int = Field(ge=1, le=9)
    unlimited: bool = False
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_source(self) -> "SpellSpecificCastGrant":
        try:
            if self.unlimited == bool(self.resource_id):
                raise ValueError("Spell-specific cast grant requires exactly one of unlimited or resource_id.")
            return self
        except Exception:
            logger.exception("Failed to validate spell-specific cast grant %s.", self.source_id)
            raise


class SpellDamageMaximizerGrant(BaseModel):
    """Optional source-owned maximization for damaging spells with repeat-use self damage."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    minimum_spell_level: int = Field(default=1, ge=1, le=9)
    maximum_spell_level: int = Field(default=5, ge=1, le=9)
    free_uses: int = Field(default=1, ge=0, le=20)
    self_damage_die_size: int = Field(default=12, ge=2, le=100)
    repeat_base_dice_per_spell_level: int = Field(default=2, ge=1, le=20)
    repeat_increment_dice_per_spell_level: int = Field(default=1, ge=0, le=20)
    self_damage_type: str = "necrotic"
    bypasses_resistance_and_immunity: bool = True

    @model_validator(mode="after")
    def validate_levels(self) -> "SpellDamageMaximizerGrant":
        try:
            if self.maximum_spell_level < self.minimum_spell_level:
                raise ValueError("Spell damage maximizer maximum level must be at least the minimum level.")
            return self
        except Exception:
            logger.exception("Failed to validate spell damage maximizer %s.", self.source_id)
            raise
