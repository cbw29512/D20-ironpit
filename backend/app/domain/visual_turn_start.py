"""Immutable source-owned parameters for generic turn-start visual saves."""
from __future__ import annotations
import logging
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator
from app.domain.save_effects import FailedSaveTimedEffect

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
    # The same visual trigger can bind a staged condition or a normal timed
    # failed-save effect. No printed ability name is used in combat dispatch.
    failed_save_timed_effect: FailedSaveTimedEffect | None = None
    required_target_creature_types: list[str] = Field(default_factory=list)
    requires_source_sight: bool = True
    requires_source_not_incapacitated: bool = True
    requires_true_form_visibility: bool = False
    source_effect_immunity_on_success: bool = False

    @model_validator(mode="after")
    def validate_semantics(self) -> "VisualTurnStartRule":
        try:
            if (not self.source_id.strip() or not self.source_name.strip()
                    or not self.initial_debuff.strip() or not self.terminal_debuff.strip()
                    or self.initial_debuff == self.terminal_debuff):
                raise ValueError("Visual rule requires source identity and distinct effect stages.")
            if self.failed_save_timed_effect is not None:
                rider = self.failed_save_timed_effect
                if (self.immediate_petrification_margin is not None
                        or rider.repeat_save_ability is None
                        or rider.repeat_save_dc != self.save_dc
                        or rider.repeat_save_timing is None
                        or not rider.source_effect_immunity_on_end
                        or not self.source_effect_immunity_on_success):
                    raise ValueError("Timed visual save requires exact repeat-save and source immunity semantics.")
            if any(not item.strip() for item in self.required_target_creature_types):
                raise ValueError("Visual creature-type qualifiers must be nonblank.")
            return self
        except ValueError:
            logger.exception("Invalid source-owned visual turn-start rule.")
            raise
