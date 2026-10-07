from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)


class DamageTakenTimedEffect(BaseModel):
    """Source-owned parameters for a timed effect triggered by typed damage."""

    source_id: str
    source_name: str
    trigger_damage_type: DamageType
    effect_id: str
    target_turns: int = Field(default=1, ge=1, le=20)
    attack_roll_disadvantage: bool = False
    ability_check_disadvantage: bool = False

    @model_validator(mode="after")
    def validate_effect(self) -> "DamageTakenTimedEffect":
        try:
            if not self.source_id.strip() or not self.source_name.strip() or not self.effect_id.strip():
                raise ValueError("Damage-triggered timed effect identifiers must be non-empty.")
            if not (self.attack_roll_disadvantage or self.ability_check_disadvantage):
                raise ValueError("Damage-triggered timed effect must change at least one roll scope.")
            return self
        except Exception:
            logger.exception("Invalid damage-triggered timed effect %s.", self.effect_id)
            raise
