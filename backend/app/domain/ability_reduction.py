from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.actions import AbilityName


class AbilityScoreReductionEffectDefinition(BaseModel):
    """Declarative on-hit reduction of one ability score."""

    kind: Literal["ability-score-reduction"] = "ability-score-reduction"
    ability: AbilityName
    dice_count: int = Field(ge=1, le=4)
    dice_size: int = Field(ge=2, le=20)
    minimum_score: int = Field(default=0, ge=0, le=30)
    dies_at_minimum: bool = False


class AbilityScoreReductionOnHit(BaseModel):
    ability: AbilityName
    dice_count: int = Field(ge=1, le=4)
    dice_size: int = Field(ge=2, le=20)
    minimum_score: int = Field(default=0, ge=0, le=30)
    dies_at_minimum: bool = False
