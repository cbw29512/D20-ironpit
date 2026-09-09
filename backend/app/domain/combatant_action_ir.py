from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.combat_ir import CombatActionIR
from app.domain.combat_sequence_ir import ActionSequenceIR


class CombatantActionIR(BaseModel):
    schema_version: Literal[1] = 1
    combatant_id: str
    primary_attack_id: str
    actions: list[CombatActionIR] = Field(min_length=1)
    attack_sequence: ActionSequenceIR | None = None

    @model_validator(mode="after")
    def validate_references(self) -> "CombatantActionIR":
        ids = {action.id for action in self.actions}
        if len(ids) != len(self.actions):
            raise ValueError("Combat action IR ids must be unique per combatant.")
        if self.primary_attack_id not in ids:
            raise ValueError("Primary attack must reference a normalized combat action.")
        if self.attack_sequence:
            for slot in self.attack_sequence.slots:
                for option in slot.options:
                    if option.action_id not in ids:
                        raise ValueError("Action sequence references an undeclared normalized action.")
        return self
