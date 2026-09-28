from __future__ import annotations

import logging
from typing import Literal

from app.domain.character_builds import AbilityName

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)

PassiveModifierKind = Literal["attacks-against-disadvantage", "condition-immunity", "targeting-save-gate"]


class PassiveModifierGrant(BaseModel):
    """Declarative always-on modifier compiled into fresh combat state."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    kind: PassiveModifierKind
    condition_id: str | None = Field(default=None, min_length=1)
    source_creature_types: list[str] = Field(default_factory=list)
    required_active_effect_ids: list[str] = Field(default_factory=list)
    save_ability: AbilityName | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    ends_on_owner_attack: bool = False
    success_immunity_hours: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_grant(self) -> "PassiveModifierGrant":
        try:
            if self.kind in {"attacks-against-disadvantage", "targeting-save-gate"} and not self.source_creature_types:
                raise ValueError("Passive source-filtered modifiers require at least one source creature type.")
            if self.kind == "condition-immunity" and not self.source_creature_types and not self.required_active_effect_ids:
                raise ValueError("Passive condition immunity requires a source filter or active-effect requirement.")
            if any(not item.strip() for item in self.source_creature_types):
                raise ValueError("Passive modifier source creature types cannot be blank.")
            if any(not item.strip() for item in self.required_active_effect_ids):
                raise ValueError("Passive modifier active-effect requirements cannot be blank.")
            if self.required_active_effect_ids and self.kind != "condition-immunity":
                raise ValueError(f"{self.kind} does not accept active-effect requirements.")
            if self.kind == "condition-immunity" and self.condition_id is None:
                raise ValueError("Passive condition immunity requires a condition id.")
            if self.kind != "condition-immunity" and self.condition_id is not None:
                raise ValueError(f"{self.kind} does not accept a condition id.")
            gate_fields = (self.save_ability, self.save_dc, self.success_immunity_hours)
            if self.kind == "targeting-save-gate":
                if self.save_ability is None or self.save_dc is None:
                    raise ValueError("Passive targeting gates require a save ability and DC.")
            elif any(item is not None for item in gate_fields) or self.ends_on_owner_attack:
                raise ValueError(f"{self.kind} does not accept targeting-gate fields.")
            normalized = [item.casefold() for item in self.source_creature_types]
            if len(set(normalized)) != len(normalized):
                raise ValueError("Passive modifier source creature types must be unique.")
            required_effects = [item.casefold() for item in self.required_active_effect_ids]
            if len(set(required_effects)) != len(required_effects):
                raise ValueError("Passive modifier active-effect requirements must be unique.")
            self.source_creature_types = normalized
            self.required_active_effect_ids = required_effects
            return self
        except Exception:
            logger.exception(
                "Invalid passive modifier grant %s (%s).",
                self.source_id,
                self.kind,
            )
            raise
