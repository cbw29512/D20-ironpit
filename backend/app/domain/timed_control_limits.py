from __future__ import annotations

import logging

from pydantic import BaseModel, Field, model_validator

from app.domain.character_builds import AbilityName

logger = logging.getLogger(__name__)


class TimedControlLimits(BaseModel):
    """Parameterized rider limits that are not a named ConditionName."""

    speed_multiplier: float = Field(default=1.0, gt=0.0, le=1.0)
    action_bonus_exclusive: bool = False
    max_attacks_per_turn: int | None = Field(default=None, ge=1, le=20)
    d20_disadvantage_abilities: list[AbilityName] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_limits(self) -> "TimedControlLimits":
        try:
            abilities = [item.strip().casefold() for item in self.d20_disadvantage_abilities]
            if any(not item for item in abilities):
                raise ValueError("Timed control D20 Disadvantage abilities must be non-empty.")
            if len(set(abilities)) != len(abilities):
                raise ValueError("Timed control D20 Disadvantage abilities must be unique.")
            self.d20_disadvantage_abilities = abilities  # type: ignore[assignment]
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
) -> TimedControlLimits | None:
    """Build limits only when a rider actually changes combat math."""
    try:
        abilities = [str(item).strip().casefold() for item in (d20_disadvantage_abilities or []) if str(item).strip()]
        if disadvantage_strength_d20_tests and "strength" not in abilities:
            abilities.append("strength")
        if (
            speed_multiplier == 1.0
            and not action_bonus_exclusive
            and max_attacks_per_turn is None
            and not abilities
        ):
            return None
        return TimedControlLimits(
            speed_multiplier=speed_multiplier,
            action_bonus_exclusive=action_bonus_exclusive,
            max_attacks_per_turn=max_attacks_per_turn,
            d20_disadvantage_abilities=abilities,  # type: ignore[arg-type]
        )
    except Exception:
        logger.exception("Failed to compile timed control limits.")
        raise
