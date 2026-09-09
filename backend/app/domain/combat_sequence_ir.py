from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ActionReferenceIR(BaseModel):
    family: Literal["attack", "save"]
    action_id: str


class ActionChoiceSlotIR(BaseModel):
    options: list[ActionReferenceIR] = Field(min_length=1, max_length=32)


class ActionSequenceIR(BaseModel):
    schema_version: Literal[1] = 1
    id: str
    name: str = "Multiattack"
    action_cost: Literal["action"] = "action"
    is_attack_action: bool = False
    slots: list[ActionChoiceSlotIR] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def require_unique_options_per_slot(self) -> "ActionSequenceIR":
        for slot in self.slots:
            keys = {(option.family, option.action_id) for option in slot.options}
            if len(keys) != len(slot.options):
                raise ValueError("Action sequence slot options must be unique.")
        return self
