from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

PassiveModifierKind = Literal["attacks-against-disadvantage", "condition-immunity"]


class PassiveModifierGrant(BaseModel):
    """Declarative always-on modifier installed into each fresh combat instance."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    kind: PassiveModifierKind
    condition_id: str | None = Field(default=None, min_length=1)
    source_creature_types: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_grant(self) -> "PassiveModifierGrant":
        if self.kind == "condition-immunity" and self.condition_id is None:
            raise ValueError("Passive condition immunity requires a condition id.")
        if self.kind != "condition-immunity" and self.condition_id is not None:
            raise ValueError(f"{self.kind} does not accept a condition id.")
        normalized = [item.casefold() for item in self.source_creature_types]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Passive modifier source creature types must be unique.")
        return self
