from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ActionCost, DamageTypeName

logger = logging.getLogger(__name__)


class TimedAuraAction(BaseModel):
    """Declarative timed self-owned aura with universal start-turn and save-defense payloads."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    action_cost: ActionCost = "action"
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1, le=200)
    duration_rounds: int = Field(ge=1, le=600)
    radius_ft: int = Field(ge=0, le=300)
    start_turn_fixed_damage: int = Field(default=0, ge=0, le=500)
    damage_type: DamageTypeName | None = None
    saving_throw_advantage_abilities: list[AbilityName] = Field(default_factory=list)
    saving_throw_advantage_source_creature_types: list[str] = Field(default_factory=list)
    saving_throw_advantage_requires_spell: bool = False
    priority: int = 0
    animation: str = "timed-aura"
    source: str | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "TimedAuraAction":
        try:
            if self.start_turn_fixed_damage and self.damage_type is None:
                raise ValueError("Timed aura start-turn damage requires a damage type.")
            if self.damage_type is not None and not self.start_turn_fixed_damage:
                raise ValueError("Timed aura damage type requires positive start-turn damage.")
            if len(set(self.saving_throw_advantage_abilities)) != len(self.saving_throw_advantage_abilities):
                raise ValueError("Timed aura save-Advantage abilities must be unique.")
            normalized = [item.casefold() for item in self.saving_throw_advantage_source_creature_types]
            if len(set(normalized)) != len(normalized):
                raise ValueError("Timed aura source creature types must be unique.")
            if not self.start_turn_fixed_damage and not self.saving_throw_advantage_abilities:
                raise ValueError("Timed aura must define a combat payload.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Timed aura schema validation failed for %s.", self.id)
            raise RuntimeError("Timed aura schema could not be validated.") from exc
