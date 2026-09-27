from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class SpellDamageMaximizerGrant(BaseModel):
    """Source-owned permission to maximize declared spell damage with escalating self damage."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    eligible_spell_ids: list[str] = Field(min_length=1)
    minimum_spell_level: int = Field(default=1, ge=1, le=9)
    maximum_spell_level: int = Field(default=5, ge=1, le=9)
    safe_uses: int = Field(default=1, ge=0, le=20)
    self_damage_dice_size: int = Field(default=12, ge=2, le=100)
    initial_self_damage_dice_per_spell_level: int = Field(default=2, ge=0, le=20)
    self_damage_increment_per_spell_level: int = Field(default=1, ge=0, le=20)
    self_damage_type: str = "necrotic"
    ignores_resistance_and_immunity: bool = True

    @model_validator(mode="after")
    def validate_grant(self) -> "SpellDamageMaximizerGrant":
        try:
            if self.maximum_spell_level < self.minimum_spell_level:
                raise ValueError("Spell damage maximizer level range is inverted.")
            ids = [item.strip() for item in self.eligible_spell_ids]
            if any(not item for item in ids) or len(set(ids)) != len(ids):
                raise ValueError("Spell damage maximizer spell ids must be unique and non-empty.")
            self.eligible_spell_ids = ids
            return self
        except Exception:
            logger.exception("Failed to validate spell damage maximizer %s.", self.source_id)
            raise
