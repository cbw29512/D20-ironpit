from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class OncePerTurnWeaponHitDamageRider(BaseModel):
    """Immutable source data for one generic once-per-turn weapon-hit damage rider."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    dice_count: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(default=2, ge=2, le=100)
    flat_bonus: int = Field(default=0, ge=0, le=30)
    damage_type: str | None = Field(default=None, min_length=1)
    requires_target_below_max_hp: bool = False
    target_creature_types: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_damage_and_targets(self) -> "OncePerTurnWeaponHitDamageRider":
        if self.dice_count == 0 and self.flat_bonus == 0:
            raise ValueError("Once-per-turn weapon-hit rider requires dice or a flat bonus.")
        normalized = [item.strip().casefold() for item in self.target_creature_types]
        if any(not item for item in normalized):
            raise ValueError("Target creature types must be non-empty.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Target creature types must be unique.")
        self.target_creature_types = normalized
        return self
