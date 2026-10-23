"""Immutable parameters for a reusable variable-head combat lifecycle."""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator


class VariableHeadProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_name: str = Field(min_length=1)
    reaction_source_name: str = Field(min_length=1)
    initial_heads: int = Field(ge=1)
    sever_damage_threshold: int = Field(ge=1)
    heads_per_regrowth: int = Field(ge=1)
    healing_per_regrown_head: int = Field(ge=0)
    regrowth_blocking_damage_types: list[str] = Field(min_length=1)
    save_advantage_conditions: list[str] = Field(default_factory=list)
    multiattack_per_head: bool = True
    extra_opportunity_reactions_per_head_beyond_one: bool = True

    @field_validator("regrowth_blocking_damage_types")
    @classmethod
    def normalize_damage_types(cls, values: list[str]) -> list[str]:
        normalized = [value.strip().lower() for value in values]
        if any(not value for value in normalized) or len(set(normalized)) != len(normalized):
            raise ValueError("Regrowth-blocking damage types must be unique nonempty values.")
        return normalized
