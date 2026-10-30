from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.rule_types import AbilityName


class OngoingHpLossEffectDefinition(BaseModel):
    """Failed-save effect that causes direct HP loss without dealing damage."""

    kind: Literal["ongoing-hp-loss"] = "ongoing-hp-loss"
    effect_id: str
    name: str
    timing: Literal["target_turn_start"] = "target_turn_start"
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    duration_rounds: int = Field(ge=1, le=100)
    ends_on_spell_healing: bool = False
    removal_ability: AbilityName | None = None
    removal_skill: str | None = None
    removal_dc: int | None = Field(default=None, ge=1, le=40)
    removal_range_ft: int = Field(default=5, ge=0, le=120)


class OngoingHpLossState(BaseModel):
    effect_id: str
    name: str
    source_id: str
    source_effect_id: str
    applied_round: int = Field(ge=1)
    expires_round: int = Field(ge=2)
    timing: Literal["target_turn_start"] = "target_turn_start"
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(ge=2, le=100)
    ends_on_spell_healing: bool = False
    removal_ability: AbilityName | None = None
    removal_skill: str | None = None
    removal_dc: int | None = Field(default=None, ge=1, le=40)
    removal_range_ft: int = Field(default=5, ge=0, le=120)
