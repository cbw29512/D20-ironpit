from __future__ import annotations

from enum import StrEnum
import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class DamageTakenTimedEffect(BaseModel):
    """Source-owned parameters for a timed effect triggered by typed damage."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    trigger_damage_type: DamageType
    effect_id: str = Field(min_length=1)
    target_turns: int = Field(default=1, ge=1, le=20)
    attack_roll_disadvantage: bool = False
    ability_check_disadvantage: bool = False

    @model_validator(mode="after")
    def validate_roll_scope(self) -> "DamageTakenTimedEffect":
        try:
            if not (self.attack_roll_disadvantage or self.ability_check_disadvantage):
                raise ValueError("Damage-triggered timed effect must change at least one roll scope.")
            return self
        except Exception:
            logger.exception("Invalid damage-triggered timed effect %s.", self.effect_id)
            raise


class DamageSourceQualifier(StrEnum):
    ATTACK = "attack"
    WEAPON = "weapon"
    MELEE = "melee"
    RANGED = "ranged"
    MAGICAL = "magical"
    SILVERED = "silvered"
    ADAMANTINE = "adamantine"


class DamageDefenseKind(StrEnum):
    RESISTANCE = "resistance"
    IMMUNITY = "immunity"
    VULNERABILITY = "vulnerability"


class ConditionalDamageDefense(BaseModel):
    """Generic defense matched against damage type plus source semantics."""

    id: str = Field(min_length=1)
    kind: DamageDefenseKind
    damage_types: list[DamageType] = Field(min_length=1)
    required_source_qualifiers: list[DamageSourceQualifier] = Field(default_factory=list)
    forbidden_source_qualifiers: list[DamageSourceQualifier] = Field(default_factory=list)
