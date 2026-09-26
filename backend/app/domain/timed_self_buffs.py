from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, ConditionName, ConditionTiming
from app.domain.debuffs import DebuffCounter
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class TimedEmanationDamage(BaseModel):
    """Fixed typed damage emitted by an active timed effect at a declared turn-start window."""

    trigger: Literal["enemy_turn_start"] = "enemy_turn_start"
    radius_ft: int = Field(ge=1, le=120)
    fixed_damage: int = Field(ge=1, le=500)
    damage_type: DamageType


class TimedFriendlySaveAura(BaseModel):
    """Live friendly aura that grants save Advantage for matching effect tags."""

    radius_ft: int = Field(ge=1, le=120)
    required_effect_tags: list[str] = Field(min_length=1)
    requires_hearing: bool = False

    @model_validator(mode="after")
    def validate_tags(self) -> "TimedFriendlySaveAura":
        tags = [item.strip().casefold() for item in self.required_effect_tags]
        if any(not item for item in tags) or len(set(tags)) != len(tags):
            raise ValueError("Timed friendly save-aura effect tags must be non-empty and unique.")
        self.required_effect_tags = tags
        return self


class TimedSelfBuffAction(BaseModel):
    """Declarative timed self effect composed from universal combat primitives."""

    id: str
    name: str
    action_cost: ActionCost = "action"
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=200)
    duration_rounds: int = Field(ge=1, le=600)
    condition_ids: list[ConditionName] = Field(default_factory=list)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    debuff_counters: list[DebuffCounter] = Field(default_factory=list)
    saving_throw_advantage_grants: list[SavingThrowAdvantageGrant] = Field(default_factory=list)
    friendly_save_advantage_aura: TimedFriendlySaveAura | None = None
    start_turn_emanation_damage: TimedEmanationDamage | None = None
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False
    expiry_timing: ConditionTiming = "source_turn_start"
    priority: int = 0
    animation: str = "buff"

    @model_validator(mode="after")
    def validate_on_turn_activation(self) -> "TimedSelfBuffAction":
        try:
            if self.action_cost == "reaction":
                raise ValueError("Timed self-buff Actions currently require an on-turn Action or Bonus Action.")
            if len(set(self.condition_ids)) != len(self.condition_ids):
                raise ValueError("Timed self-buff condition ids must be unique.")
            if len(set(self.damage_resistances)) != len(self.damage_resistances):
                raise ValueError("Timed self-buff damage resistances must be unique.")
            counter_keys = {
                (item.debuff_id, item.source_scope, item.mode, item.movement_cost_ft)
                for item in self.debuff_counters
            }
            if len(counter_keys) != len(self.debuff_counters):
                raise ValueError("Timed self-buff debuff counters must be unique.")
            grant_keys = {
                (
                    item.source_id,
                    tuple(item.abilities),
                    item.requires_magical_effect,
                    item.requires_spell_effect,
                    tuple(item.source_creature_types),
                )
                for item in self.saving_throw_advantage_grants
            }
            if len(grant_keys) != len(self.saving_throw_advantage_grants):
                raise ValueError("Timed self-buff saving-throw Advantage grants must be unique.")
            if not (
                self.condition_ids
                or self.damage_resistances
                or self.debuff_counters
                or self.saving_throw_advantage_grants
                or self.friendly_save_advantage_aura is not None
                or self.start_turn_emanation_damage is not None
            ):
                raise ValueError("Timed self-buff requires at least one combat effect.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Timed self-buff schema validation failed for %s.", self.id)
            raise RuntimeError("Timed self-buff schema could not be validated.") from exc
