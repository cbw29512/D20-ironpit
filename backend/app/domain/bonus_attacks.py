from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons import OnHitConditionSave

logger = logging.getLogger(__name__)


class BonusAttackGrant(BaseModel):
    """Declarative grant for one Bonus Action that makes one or more listed attacks."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    attack_ids: list[str] = Field(min_length=1, max_length=16)
    attack_count: int = Field(default=1, ge=1, le=8)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    priority: int = Field(default=100, ge=0, le=1000)
    on_hit_condition_save: OnHitConditionSave | None = None

    @model_validator(mode="after")
    def validate_attack_ids(self) -> "BonusAttackGrant":
        try:
            normalized = [attack_id.strip() for attack_id in self.attack_ids]
            if any(not attack_id for attack_id in normalized):
                raise ValueError("Bonus attack grant attack IDs must be non-empty.")
            if len(set(normalized)) != len(normalized):
                raise ValueError("Bonus attack grant attack IDs must be unique.")
            self.attack_ids = normalized
            return self
        except ValueError:
            logger.exception("Invalid Bonus Attack grant %s.", self.id)
            raise
        except Exception as exc:
            logger.exception("Failed to validate Bonus Attack grant %s.", self.id)
            raise RuntimeError("Bonus Attack grant validation failed.") from exc
