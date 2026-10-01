from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class BonusAttackGrant(BaseModel):
    """Declarative grant for one Bonus Action that makes one or more listed attacks."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    attack_ids: list[str] = Field(min_length=1, max_length=16)
    attack_count: int = Field(default=1, ge=1, le=8)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    priority: int = Field(default=100, ge=0, le=1000)

    @model_validator(mode="after")
    def validate_attack_ids(self) -> "BonusAttackGrant":
        normalized = [attack_id.strip() for attack_id in self.attack_ids]
        if any(not attack_id for attack_id in normalized):
            raise ValueError("Bonus attack grant attack IDs must be non-empty.")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Bonus attack grant attack IDs must be unique.")
        self.attack_ids = normalized
        return self
