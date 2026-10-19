"""Immutable source-owned parameters for generic turn-start visual saves."""
from __future__ import annotations
import logging
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

logger = logging.getLogger(__name__)
SaveAbility = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


class VisualTurnStartRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    range_ft: StrictInt = Field(gt=0)
    save_dc: StrictInt = Field(ge=1, le=40)
    save_ability: SaveAbility = "constitution"
    immediate_petrification_margin: StrictInt | None = Field(default=None, gt=0)
    initial_debuff: str = Field(default="restrained", min_length=1)
    terminal_debuff: str = Field(default="petrified", min_length=1)

    @model_validator(mode="after")
    def validate_semantics(self) -> "VisualTurnStartRule":
        try:
            if (not self.source_id.strip() or not self.source_name.strip()
                    or not self.initial_debuff.strip() or not self.terminal_debuff.strip()
                    or self.initial_debuff == self.terminal_debuff):
                raise ValueError("Visual rule requires source identity and distinct effect stages.")
            return self
        except ValueError:
            logger.exception("Invalid source-owned visual turn-start rule.")
            raise
