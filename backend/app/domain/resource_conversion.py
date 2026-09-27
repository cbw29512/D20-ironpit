from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

ResourceConversionAutomation = Literal["manual", "when-all-spell-slots-empty"]


class ResourceConversionAction(BaseModel):
    """Declarative exchange between two finite combat resources."""

    id: str
    name: str
    action_cost: Literal["action", "bonus_action"]
    source_resource_id: str
    source_cost: int = Field(ge=1)
    target_resource_id: str
    target_gain: int = Field(ge=1)
    target_allows_overflow: bool = False
    automation: ResourceConversionAutomation = "manual"
    priority: int = 0
    source: str | None = None

    @model_validator(mode="after")
    def validate_exchange(self) -> "ResourceConversionAction":
        if self.source_resource_id == self.target_resource_id:
            raise ValueError("Resource conversion source and target must be different resources.")
        if self.automation == "when-all-spell-slots-empty" and not self.target_resource_id.startswith("spell-slot-"):
            raise ValueError("Spell-slot-empty automation must create a spell-slot resource.")
        return self
