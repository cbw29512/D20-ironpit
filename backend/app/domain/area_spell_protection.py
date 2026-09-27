from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


class AreaSpellAllyProtectionGrant(BaseModel):
    """Source-owned permission to spare allies caught in an eligible area save spell."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    eligible_spell_ids: list[str] = Field(min_length=1)
    base_protected_allies: int = Field(default=1, ge=0, le=20)
    protected_allies_per_slot_level: int = Field(default=1, ge=0, le=20)
    requires_source_sight: bool = True
    auto_success_save: bool = True
    no_damage_on_success: bool = True

    @model_validator(mode="after")
    def validate_spell_ids(self) -> "AreaSpellAllyProtectionGrant":
        try:
            normalized = [item.strip() for item in self.eligible_spell_ids]
            if any(not item for item in normalized):
                raise ValueError("Area-spell protection spell ids must be non-empty.")
            if len(set(normalized)) != len(normalized):
                raise ValueError("Area-spell protection spell ids must be unique.")
            self.eligible_spell_ids = normalized
            if not self.auto_success_save or not self.no_damage_on_success:
                raise ValueError(
                    "Current universal area-spell protection requires automatic save success and no damage."
                )
            return self
        except Exception:
            logger.exception("Failed to validate area-spell ally protection grant %s.", self.source_id)
            raise
