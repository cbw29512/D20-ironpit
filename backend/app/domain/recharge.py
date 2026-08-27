from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class RechargeDefinition(BaseModel):
    die_size: int = Field(default=6, ge=2, le=100)
    min_roll: int = Field(ge=1)
    max_roll: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_range(self) -> "RechargeDefinition":
        if self.min_roll > self.max_roll:
            raise ValueError("Recharge minimum cannot exceed maximum.")
        if self.max_roll > self.die_size:
            raise ValueError("Recharge maximum cannot exceed die size.")
        return self


class RechargeState(BaseModel):
    feature_id: str = Field(min_length=1)
    available: bool = True
    die_size: int = Field(default=6, ge=2, le=100)
    min_roll: int = Field(ge=1)
    max_roll: int = Field(ge=1)
