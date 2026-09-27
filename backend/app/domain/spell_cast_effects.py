from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class SpellCastTimedResistance(BaseModel):
    """Optional resource-backed resistance activated by casting a matching damage spell."""

    id: str
    name: str
    qualifying_damage_type: DamageType
    resistance_damage_type: DamageType
    resource_id: str
    resource_cost: int = Field(default=1, ge=1, le=200)
    duration_rounds: int = Field(default=600, ge=1, le=6000)
    priority: int = 0

    @model_validator(mode="after")
    def validate_effect(self) -> "SpellCastTimedResistance":
        try:
            if not self.resource_id.strip():
                raise ValueError("Spell-cast resistance requires a resource id.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Spell-cast timed resistance validation failed for %s.", self.id)
            raise RuntimeError("Spell-cast timed resistance could not be validated.") from exc
