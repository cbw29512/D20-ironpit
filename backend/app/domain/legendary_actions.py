from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import SavingThrowAction


LegendaryActionKind = Literal["attack", "save", "ability_check"]


class LegendaryActionOption(BaseModel):
    id: str
    name: str
    cost: int = Field(default=1, ge=1, le=3)
    kind: LegendaryActionKind
    attack_id: str | None = None
    save_action: SavingThrowAction | None = None
    check_ability: str | None = None
    check_skill: str | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "LegendaryActionOption":
        if self.kind == "attack" and not self.attack_id:
            raise ValueError("Legendary attack requires attack_id.")
        if self.kind == "save" and self.save_action is None:
            raise ValueError("Legendary save requires save_action.")
        if self.kind == "ability_check" and not self.check_ability:
            raise ValueError("Legendary ability check requires check_ability.")
        return self
