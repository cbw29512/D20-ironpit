from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class FriendlyDefensiveAuraGrant(BaseModel):
    """Source-owned live ally aura that grants temporary defensive flat benefits."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    radius_ft: int = Field(ge=0, le=120)
    required_source_effect_id: str = Field(min_length=1)
    armor_class_bonus: int = Field(default=0, ge=0, le=20)
    saving_throw_bonus: int = Field(default=0, ge=0, le=20)
    saving_throw_abilities: list[str] = Field(default_factory=list)
    non_stacking_group: str = Field(min_length=1)
    inactive_while_incapacitated: bool = False
    inactive_while_unconscious: bool = False

    @model_validator(mode="after")
    def validate_defense(self) -> "FriendlyDefensiveAuraGrant":
        if self.armor_class_bonus == 0 and self.saving_throw_bonus == 0:
            raise ValueError("Friendly defensive aura requires an AC or saving-throw bonus.")
        if self.saving_throw_bonus and not self.saving_throw_abilities:
            raise ValueError("Saving-throw aura bonus requires at least one ability.")
        if not self.saving_throw_bonus and self.saving_throw_abilities:
            raise ValueError("Saving-throw abilities require a nonzero saving-throw bonus.")
        normalized = [item.strip().casefold() for item in self.saving_throw_abilities]
        if any(not item for item in normalized) or len(set(normalized)) != len(normalized):
            raise ValueError("Saving-throw aura abilities must be non-empty and unique.")
        self.saving_throw_abilities = normalized
        self.non_stacking_group = self.non_stacking_group.strip().casefold()
        return self
