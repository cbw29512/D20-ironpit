"""Generic per-fight link recording who controls whose body.

This is ownership data only. It does not grant attacks, suppress actions,
change teams, alter visibility, or bypass normal action/target legality.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class BodyControlLink(BaseModel):
    source_id: str = Field(min_length=1)
    source_action_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    host_id: str = Field(min_length=1)
    started_round: int = Field(ge=1)

    @model_validator(mode="after")
    def reject_self_control(self) -> "BodyControlLink":
        if self.source_id == self.host_id:
            raise ValueError("A body-control link requires distinct participants.")
        return self
