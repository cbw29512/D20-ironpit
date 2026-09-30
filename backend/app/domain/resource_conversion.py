from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

ResourceConversionAutomation = Literal["manual", "when-all-spell-slots-empty"]


class ResourceConversionAction(BaseModel):
    """Declarative exchange between two finite combat resources."""

    id: str
    name: str
    action_cost: Literal["action", "bonus_action", "none"]
    source_resource_id: str
    source_cost: int = Field(ge=1)
    additional_source_costs: dict[str, int] = Field(default_factory=dict)
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
        if self.target_resource_id in self.additional_source_costs:
            raise ValueError("Resource conversion target cannot also be an additional source resource.")
        if self.source_resource_id in self.additional_source_costs:
            raise ValueError("Primary resource conversion source cannot also be an additional source resource.")
        if any(cost < 1 for cost in self.additional_source_costs.values()):
            raise ValueError("Additional resource conversion costs must be positive integers.")
        if self.automation == "when-all-spell-slots-empty" and not self.target_resource_id.startswith("spell-slot-"):
            raise ValueError("Spell-slot-empty automation must create a spell-slot resource.")
        return self
