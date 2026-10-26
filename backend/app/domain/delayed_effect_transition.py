from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DelayedTimedEffectTransition(BaseModel):
    """Immutable card parameters for a fight-local target-turn transition."""

    model_config = ConfigDict(extra="forbid")

    target_turns: int = Field(ge=1, le=600)
    cannot_regain_hit_points: bool = False
    removal_effect_tag: str | None = None
    minimum_removal_spell_level: int = Field(default=0, ge=0, le=9)
    removal_action_exceptions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_transition(self) -> "DelayedTimedEffectTransition":
        if self.minimum_removal_spell_level and not self.removal_effect_tag:
            raise ValueError("Minimum removal spell level requires an effect tag.")
        if self.removal_effect_tag is not None and not self.removal_effect_tag.strip():
            raise ValueError("Removal effect tag cannot be blank.")
        if any(not item.strip() for item in self.removal_action_exceptions):
            raise ValueError("Removal action exceptions must be nonblank.")
        return self
