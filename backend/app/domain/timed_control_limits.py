from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.character_builds import AbilityName

logger = logging.getLogger(__name__)


class TimedSaveFlatBonus(BaseModel):
    """One ability-scoped flat saving-throw bonus or penalty owned by a timed rider."""

    ability: AbilityName
    flat_bonus: int

    @model_validator(mode="after")
    def validate_bonus(self) -> "TimedSaveFlatBonus":
        try:
            if self.flat_bonus == 0:
                raise ValueError("Timed save flat bonus cannot be zero.")
            self.ability = str(self.ability).strip().casefold()  # type: ignore[assignment]
            if not self.ability:
                raise ValueError("Timed save flat bonus requires an ability.")
            return self
        except Exception:
            logger.exception("Timed save flat bonus could not be validated.")
            raise


class TimedControlLimits(BaseModel):
    """Parameterized rider limits that are not a named ConditionName."""

    speed_multiplier: float = Field(default=1.0, gt=0.0, le=1.0)
    action_bonus_exclusive: bool = False
    max_attacks_per_turn: int | None = Field(default=None, ge=1, le=20)
    d20_disadvantage_abilities: list[AbilityName] = Field(default_factory=list)
    attack_roll_disadvantage: bool = False
    ability_check_disadvantage: bool = False
    armor_class_bonus: int = 0
    saving_throw_flat_bonuses: list[TimedSaveFlatBonus] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_limits(self) -> "TimedControlLimits":
        try:
            abilities = [item.strip().casefold() for item in self.d20_disadvantage_abilities]
            if any(not item for item in abilities):
                raise ValueError("Timed control D20 Disadvantage abilities must be non-empty.")
            if len(set(abilities)) != len(abilities):
                raise ValueError("Timed control D20 Disadvantage abilities must be unique.")
            self.d20_disadvantage_abilities = abilities  # type: ignore[assignment]
            save_keys = [item.ability for item in self.saving_throw_flat_bonuses]
            if len(set(save_keys)) != len(save_keys):
                raise ValueError("Timed control save flat bonuses must be unique per ability.")
            return self
        except Exception:
            logger.exception("Timed control limits could not be validated.")
            raise


def compiled_control_limits(
    *,
    speed_multiplier: float = 1.0,
    action_bonus_exclusive: bool = False,
    max_attacks_per_turn: int | None = None,
    d20_disadvantage_abilities: list[str] | None = None,
    disadvantage_strength_d20_tests: bool = False,
    attack_roll_disadvantage: bool = False,
    ability_check_disadvantage: bool = False,
    armor_class_bonus: int = 0,
    saving_throw_flat_bonuses: list[object] | None = None,
) -> TimedControlLimits | None:
    """Build limits only when a rider actually changes combat math."""
    try:
        abilities = [str(item).strip().casefold() for item in (d20_disadvantage_abilities or []) if str(item).strip()]
        if disadvantage_strength_d20_tests and "strength" not in abilities:
            abilities.append("strength")
        save_bonuses = [
            item if isinstance(item, TimedSaveFlatBonus) else TimedSaveFlatBonus.model_validate(item)
            for item in (saving_throw_flat_bonuses or [])
        ]
        if (
            speed_multiplier == 1.0
            and not action_bonus_exclusive
            and max_attacks_per_turn is None
            and not abilities
            and not attack_roll_disadvantage
            and not ability_check_disadvantage
            and armor_class_bonus == 0
            and not save_bonuses
        ):
            return None
        return TimedControlLimits(
            speed_multiplier=speed_multiplier,
            action_bonus_exclusive=action_bonus_exclusive,
            max_attacks_per_turn=max_attacks_per_turn,
            d20_disadvantage_abilities=abilities,  # type: ignore[arg-type]
            attack_roll_disadvantage=attack_roll_disadvantage,
            ability_check_disadvantage=ability_check_disadvantage,
            armor_class_bonus=armor_class_bonus,
            saving_throw_flat_bonuses=save_bonuses,
        )
    except Exception:
        logger.exception("Failed to compile timed control limits.")
        raise
