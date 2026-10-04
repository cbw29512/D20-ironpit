from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.domain.action_types import AbilityName, ConditionName, ConditionTiming


class MeleeHitSaveRetaliation(BaseModel):
    """Save-or-condition when a matching melee attacker hits an aura-protected creature."""

    attacker_creature_types: list[str] = Field(min_length=1)
    save_ability: AbilityName
    save_dc: int = Field(ge=1, le=40)
    condition_id: ConditionName
    expiry_timing: ConditionTiming = "target_turn_end"
    duration_rounds: int = Field(default=1, ge=1, le=10)
    magical_effect: bool = True
    bind_to_source_effect: bool = False

    @field_validator("attacker_creature_types")
    @classmethod
    def normalize_creature_types(cls, value: list[str]) -> list[str]:
        normalized = [item.strip().casefold() for item in value]
        if any(not item for item in normalized) or len(set(normalized)) != len(normalized):
            raise ValueError("Melee-hit save retaliation creature types must be unique and non-empty.")
        return normalized
