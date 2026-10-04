from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import SavingThrowAction


class LegendaryHealSpec(BaseModel):
    """Printed self-heal paid from the shared legendary-action pool."""

    dice_count: int = Field(ge=0, le=40)
    dice_size: int = Field(default=8, ge=2, le=100)
    healing_bonus: int = Field(default=0, ge=0)


class LegendaryAcBuffSpec(BaseModel):
    """Printed AC bonus that lasts until the end of the source's next turn."""

    ac_bonus: int = Field(ge=1, le=10)
    range_ft: int = Field(default=60, ge=0)


class LegendaryActionOption(BaseModel):
    """One printed legendary action that spends the shared after-turn pool."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    cost: int = Field(default=1, ge=1, le=6)
    kind: Literal["attack", "save", "heal", "ac_buff", "check"] = "attack"
    attack_id: str | None = Field(default=None, min_length=1)
    save_action: SavingThrowAction | None = None
    heal: LegendaryHealSpec | None = None
    ac_buff: LegendaryAcBuffSpec | None = None
    check_ability: str | None = Field(default=None, min_length=1)
    check_skill: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_kind(self) -> "LegendaryActionOption":
        extras = {
            "save_action": self.save_action is not None,
            "heal": self.heal is not None,
            "ac_buff": self.ac_buff is not None,
            "attack_id": self.attack_id is not None,
            "check": self.check_ability is not None or self.check_skill is not None,
        }
        if self.kind == "attack":
            if not self.attack_id:
                raise ValueError("Attack-kind legendary action requires attack_id.")
            if extras["save_action"] or extras["heal"] or extras["ac_buff"] or extras["check"]:
                raise ValueError("Attack-kind legendary action cannot carry another payload.")
        if self.kind == "save":
            if self.save_action is None or self.save_action.area is None:
                raise ValueError("Save-kind legendary action requires an area save action.")
            if extras["attack_id"] or extras["heal"] or extras["ac_buff"] or extras["check"]:
                raise ValueError("Save-kind legendary action cannot carry another payload.")
        if self.kind == "heal":
            if self.heal is None:
                raise ValueError("Heal-kind legendary action requires a heal spec.")
            if extras["attack_id"] or extras["save_action"] or extras["ac_buff"] or extras["check"]:
                raise ValueError("Heal-kind legendary action cannot carry another payload.")
        if self.kind == "ac_buff":
            if self.ac_buff is None:
                raise ValueError("AC-buff legendary action requires an AC buff spec.")
            if extras["attack_id"] or extras["save_action"] or extras["heal"] or extras["check"]:
                raise ValueError("AC-buff legendary action cannot carry another payload.")
        if self.kind == "check":
            if not self.check_ability:
                raise ValueError("Check-kind legendary action requires check_ability.")
            if extras["attack_id"] or extras["save_action"] or extras["heal"] or extras["ac_buff"]:
                raise ValueError("Check-kind legendary action cannot carry another payload.")
        return self
