from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_serializer, model_validator

from app.domain.character_builds import AbilityName
from app.domain.timed_control_limits import TimedControlLimits, TimedSaveFlatBonus, compiled_control_limits

logger = logging.getLogger(__name__)

SaveEffectTiming = Literal[
    "source_turn_start",
    "source_turn_end",
    "target_turn_start",
    "target_turn_end",
]


class FailedSaveTimedEffect(BaseModel):
    """Source-neutral timed rider applied only after a failed saving throw."""

    effect_id: str
    duration_rounds: int | None = Field(default=None, ge=1, le=100800)
    expiry_timing: SaveEffectTiming = "target_turn_end"
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: SaveEffectTiming | None = None
    next_attack_disadvantage: bool = False
    turn_behavior: Literal["normal", "forced_retreat", "single_activity"] = "normal"
    ends_on_damage: bool = False
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False
    repeat_save_failures_to_lock: int | None = Field(default=None, ge=1, le=10)
    escape_check_ability: AbilityName | None = None
    escape_check_dc: int | None = Field(default=None, ge=1, le=40)
    ground_contact: bool = False
    ends_on_teleport: bool = False
    source_effect_immunity_on_end: bool = False
    speed_multiplier: float = Field(default=1.0, gt=0.0, le=1.0)
    blocks_reactions: bool = False
    action_bonus_exclusive: bool = False
    max_attacks_per_turn: int | None = Field(default=None, ge=1, le=20)
    d20_disadvantage_abilities: list[AbilityName] = Field(default_factory=list)
    disadvantage_strength_d20_tests: bool = False
    armor_class_bonus: int = 0
    saving_throw_flat_bonuses: list[TimedSaveFlatBonus] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def serialize_without_default_control_limits(self, handler):
        """Keep unused Slow/Weaken keys out of generated capability dumps."""
        try:
            data = handler(self)
            defaults = {
                "speed_multiplier": 1.0,
                "blocks_reactions": False,
                "action_bonus_exclusive": False,
                "max_attacks_per_turn": None,
                "d20_disadvantage_abilities": [],
                "disadvantage_strength_d20_tests": False,
                "armor_class_bonus": 0,
                "saving_throw_flat_bonuses": [],
            }
            for key, default in defaults.items():
                if data.get(key) == default:
                    data.pop(key, None)
            return data
        except Exception:
            logger.exception("Failed to serialize failed-save timed rider %s.", self.effect_id)
            raise

    def compiled_limits(self) -> TimedControlLimits | None:
        return compiled_control_limits(
            speed_multiplier=self.speed_multiplier,
            action_bonus_exclusive=self.action_bonus_exclusive,
            max_attacks_per_turn=self.max_attacks_per_turn,
            d20_disadvantage_abilities=list(self.d20_disadvantage_abilities),
            disadvantage_strength_d20_tests=self.disadvantage_strength_d20_tests,
            armor_class_bonus=self.armor_class_bonus,
            saving_throw_flat_bonuses=list(self.saving_throw_flat_bonuses),
        )

    @model_validator(mode="after")
    def validate_repeat_save(self) -> "FailedSaveTimedEffect":
        try:
            configured = (
                self.repeat_save_ability is not None,
                self.repeat_save_dc is not None,
                self.repeat_save_timing is not None,
            )
            if any(configured) and not all(configured):
                raise ValueError("Repeat-save riders require ability, DC, and timing together.")
            if (self.escape_check_ability is None) != (self.escape_check_dc is None):
                raise ValueError("Escape-check riders require ability and DC together.")
            return self
        except Exception:
            logger.exception(
                "Failed to validate failed-save timed rider for effect %s.",
                self.effect_id,
            )
            raise
