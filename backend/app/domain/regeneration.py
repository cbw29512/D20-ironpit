from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from app.domain.weapons_base import DamageType
from app.domain.environment_contexts import EnvironmentContextId

logger = logging.getLogger(__name__)


class RegenerationTrait(BaseModel):
    """Declarative start-of-turn hit-point restoration with optional damage-type suppression."""

    amount: int = Field(ge=1, le=200)
    requires_positive_hp: bool = False
    suppressed_by_damage_types: list[DamageType] = Field(default_factory=list)
    suppressed_by_environment_contexts: list[EnvironmentContextId] = Field(
        default_factory=list, exclude_if=lambda values: not values,
    )
    survives_zero_until_turn: bool = False
    source_name: str = "Regeneration"

    def suppressed_by(self, damage_types: set[str] | set[DamageType]) -> bool:
        try:
            taken = {str(item) for item in damage_types}
            return any(item.value in taken for item in self.suppressed_by_damage_types)
        except Exception:
            logger.exception("Failed to evaluate Regeneration suppression for %s.", self.source_name)
            raise
