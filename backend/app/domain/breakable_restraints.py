"""Universal breakable object carried by a temporary condition, never a card."""
from __future__ import annotations

import logging
from pydantic import BaseModel, Field, model_validator
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class BreakableObjectSpec(BaseModel):
    """Source-owned durability, vulnerabilities and immunities for an attached snare."""

    armor_class: int = Field(ge=1, le=40)
    hit_points: int = Field(ge=1)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_defenses(self) -> "BreakableObjectSpec":
        try:
            if (len(set(self.damage_vulnerabilities)) != len(self.damage_vulnerabilities)
                    or len(set(self.damage_immunities)) != len(self.damage_immunities)
                    or set(self.damage_vulnerabilities) & set(self.damage_immunities)):
                raise ValueError("Breakable-object vulnerabilities and immunities must not overlap.")
            return self
        except Exception:
            logger.exception("Invalid breakable object defenses.")
            raise


class BreakableObjectState(BaseModel):
    """Per-fight, per-target object HP; source and template are immutable."""

    armor_class: int = Field(ge=1, le=40)
    current_hp: int = Field(ge=0)
    damage_vulnerabilities: list[DamageType] = Field(default_factory=list)
    damage_immunities: list[DamageType] = Field(default_factory=list)

    @classmethod
    def from_spec(cls, spec: BreakableObjectSpec) -> "BreakableObjectState":
        try:
            return cls(
                armor_class=spec.armor_class, current_hp=spec.hit_points,
                damage_vulnerabilities=list(spec.damage_vulnerabilities),
                damage_immunities=list(spec.damage_immunities),
            )
        except Exception:
            logger.exception("Failed to instantiate a fresh breakable condition object.")
            raise
