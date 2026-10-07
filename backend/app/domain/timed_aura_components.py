from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, ConditionTiming
from app.domain.melee_hit_save_retaliation import MeleeHitSaveRetaliation
from app.domain.timed_control_limits import TimedControlLimits
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class TimedEmanationDamage(BaseModel):
    """Typed emanation damage emitted by an active timed effect at a declared window."""

    trigger: Literal["enemy_turn_start", "enter_or_start"] = "enemy_turn_start"
    radius_ft: int = Field(ge=1, le=120)
    fixed_damage: int = Field(default=0, ge=0, le=500)
    dice_count: int = Field(default=0, ge=0, le=40)
    dice_size: int = Field(default=8, ge=2, le=100)
    damage_type: DamageType
    save_ability: str | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    success_damage: Literal["none", "half"] = "none"
    speed_multiplier: float = Field(default=1.0, gt=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_emanation(self) -> "TimedEmanationDamage":
        try:
            if self.fixed_damage <= 0 and self.dice_count <= 0:
                raise ValueError("Emanation damage requires fixed damage or dice.")
            if (self.save_ability is None) != (self.save_dc is None):
                raise ValueError("Emanation save damage requires both save ability and DC.")
            return self
        except Exception:
            logger.exception("Timed emanation damage schema validation failed.")
            raise


class TimedHostileConditionAura(BaseModel):
    """Hostile live aura that makes a save at the declared turn-start window."""

    trigger: Literal["enemy_turn_start"] = "enemy_turn_start"
    radius_ft: int = Field(ge=1, le=120)
    save_ability: AbilityName
    save_dc: int = Field(ge=1, le=40)
    condition_id: ConditionName
    success_immunity: bool = False
    source_is_magical: bool = True
    # Target lifetime is independent of the source aura lifetime.
    condition_duration_rounds: int | None = Field(default=None, ge=1, le=600)
    condition_expiry_timing: ConditionTiming | None = None
    recipient_scope: Literal["enemies", "all"] = "enemies"
    suppress_reactions: bool = False
    control_limits: TimedControlLimits | None = None
    effect_tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_condition_aura(self) -> "TimedHostileConditionAura":
        try:
            tags = [tag.strip().casefold() for tag in self.effect_tags]
            if any(not tag for tag in tags) or len(set(tags)) != len(tags):
                raise ValueError("Condition-aura effect tags must be non-empty and unique.")
            if self.condition_duration_rounds is not None and self.condition_expiry_timing is None:
                raise ValueError("A condition-aura duration requires an explicit expiry window.")
            self.effect_tags = tags
            return self
        except Exception:
            logger.exception("Condition-aura schema validation failed.")
            raise


class TimedFriendlyCoverAura(BaseModel):
    """Live friendly aura that grants one non-stacking cover benefit."""

    radius_ft: int = Field(ge=1, le=120)
    cover_bonus: Literal[2, 5]


class TimedFriendlySaveAura(BaseModel):
    """Live friendly aura that grants save Advantage for matching effect tags."""

    radius_ft: int = Field(ge=1, le=120)
    required_effect_tags: list[str] = Field(default_factory=list)
    requires_hearing: bool = False
    all_saves: bool = False
    attacks_against_disadvantage: bool = False
    target_template_ids: list[str] = Field(default_factory=list)
    includes_source: bool = False
    recipient_scope: Literal["allies", "all"] = "allies"
    covers_arena: bool = False
    melee_hit_save_retaliation: MeleeHitSaveRetaliation | None = None

    @model_validator(mode="after")
    def validate_tags(self) -> "TimedFriendlySaveAura":
        try:
            ids = self.target_template_ids
            if any(not value.strip() for value in ids) or len(set(ids)) != len(ids):
                raise ValueError("Friendly aura recipient template IDs must be non-empty and unique.")
            tags = [item.strip().casefold() for item in self.required_effect_tags]
            if any(not item for item in tags) or len(set(tags)) != len(tags):
                raise ValueError("Timed friendly save-aura effect tags must be non-empty and unique.")
            if self.all_saves and tags:
                raise ValueError("All-save auras cannot also require effect tags.")
            if not self.all_saves and not tags and not self.attacks_against_disadvantage:
                raise ValueError("Timed friendly save-aura requires tags, all-saves, or attacks-against Disadvantage.")
            self.required_effect_tags = tags
            return self
        except Exception:
            logger.exception("Failed friendly save-aura schema validation.")
            raise
