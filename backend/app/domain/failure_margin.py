"""Declarative on-hit save escalation; never keyed to a printed ability name."""
from __future__ import annotations

import logging

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.action_types import ConditionName


class FailureMarginEscalation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    margin: int = Field(ge=1, le=20)
    additional_condition_ids: list[ConditionName] = Field(min_length=1)
    replacement_duration_dice_count: int | None = Field(default=None, ge=1, le=20)
    replacement_duration_dice_size: int | None = Field(default=None, ge=2, le=100)
    replacement_duration_round_multiplier: int | None = Field(default=None, ge=1, le=100)
    ends_on_damage: bool = False
    allowed_removal_action_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_duration_dice(self) -> "FailureMarginEscalation":
        configured = (
            self.replacement_duration_dice_count is not None,
            self.replacement_duration_dice_size is not None,
            self.replacement_duration_round_multiplier is not None,
        )
        if any(configured) and not all(configured):
            raise ValueError("Replacement duration requires count, size, and round multiplier.")
        if len(set(self.additional_condition_ids)) != len(self.additional_condition_ids):
            raise ValueError("Escalated condition IDs must be unique.")
        return self

logger = logging.getLogger(__name__)


def require_escalation_duration(
    rule: FailureMarginEscalation | None,
    duration_rounds: int | None,
) -> None:
    """Reject a source card whose escalated conditions cannot expire."""
    try:
        if (
            rule is not None
            and duration_rounds is None
            and rule.replacement_duration_dice_count is None
        ):
            raise ValueError(
                "Failed-save escalation requires duration_rounds or replacement duration dice."
            )
    except ValueError:
        logger.warning("Rejected failed-save escalation without an expiry duration.")
        raise
    except Exception:
        logger.exception("Failed to validate failed-save escalation duration.")
        raise
