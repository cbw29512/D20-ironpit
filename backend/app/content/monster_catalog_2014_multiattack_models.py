from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.size import CreatureSize

MultiattackRequirement2014 = Literal[
    "source_has_grappled_target",
    "action_available",
]
MultiattackFollowUpCondition2014 = Literal["all_attacks_hit_same_target"]


class CatalogMultiattackBindingSlot2014(BaseModel):
    """One ordered source-level Multiattack step before runtime action resolution."""

    action_ids: list[str] = Field(min_length=1, max_length=16)
    optional: bool = False
    requirement: MultiattackRequirement2014 | None = None


class CatalogMultiattackBinding2014(BaseModel):
    """Source-faithful binding for Multiattacks that reference unresolved mechanics."""

    slots: list[CatalogMultiattackBindingSlot2014] = Field(min_length=1, max_length=8)
    repeat_slot_index: int | None = Field(default=None, ge=0, le=7)
    repeat_count_source: str | None = None
    follow_up_action_id: str | None = None
    follow_up_condition: MultiattackFollowUpCondition2014 | None = None
    follow_up_grapple_escape_dc: int | None = Field(default=None, ge=1, le=40)
    follow_up_max_target_size: CreatureSize | None = None

    @model_validator(mode="after")
    def validate_dependent_fields(self) -> "CatalogMultiattackBinding2014":
        repeat_fields = (self.repeat_slot_index, self.repeat_count_source)
        if any(value is not None for value in repeat_fields) and not all(value is not None for value in repeat_fields):
            raise ValueError("Dynamic Multiattack repetition requires both a slot and a count source.")
        follow_up_fields = (self.follow_up_action_id, self.follow_up_condition)
        if any(value is not None for value in follow_up_fields) and not all(value is not None for value in follow_up_fields):
            raise ValueError("Multiattack follow-up action and trigger condition must be declared together.")
        if self.follow_up_grapple_escape_dc is not None and self.follow_up_action_id is None:
            raise ValueError("Follow-up grapple data requires a follow-up action.")
        if self.follow_up_max_target_size is not None and self.follow_up_action_id is None:
            raise ValueError("Follow-up size data requires a follow-up action.")
        if self.repeat_slot_index is not None and self.repeat_slot_index >= len(self.slots):
            raise ValueError("Dynamic Multiattack repeat slot must reference an existing slot.")
        return self
