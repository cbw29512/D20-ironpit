from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class EnvironmentContextReaction(BaseModel):
    """Target-owned response to a universal battlefield context tag."""

    context_tag: str = Field(min_length=1)
    attack_roll_disadvantage: bool = False
    ability_check_disadvantage: bool = False

    @model_validator(mode="after")
    def validate_reaction(self) -> "EnvironmentContextReaction":
        self.context_tag = self.context_tag.strip().casefold()
        if not self.context_tag:
            raise ValueError("Environment context reaction tag must be non-empty.")
        if not (self.attack_roll_disadvantage or self.ability_check_disadvantage):
            raise ValueError("Environment context reaction must change at least one combat outcome.")
        return self


class TimedEnvironmentContextAura(BaseModel):
    """Source-owned timed area that supplies universal battlefield context tags."""

    radius_ft: int = Field(ge=1, le=120)
    context_tags: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_tags(self) -> "TimedEnvironmentContextAura":
        tags = [item.strip().casefold() for item in self.context_tags]
        if any(not item for item in tags) or len(set(tags)) != len(tags):
            raise ValueError("Environment context aura tags must be non-empty and unique.")
        self.context_tags = tags
        return self
