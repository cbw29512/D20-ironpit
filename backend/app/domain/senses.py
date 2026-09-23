from __future__ import annotations

from pydantic import BaseModel, Field


class CombatSenses(BaseModel):
    """Source-neutral senses that can affect combat visibility and detection."""

    darkvision_ft: int = Field(default=0, ge=0)
    blindsight_ft: int = Field(default=0, ge=0)
    truesight_ft: int = Field(default=0, ge=0)
    tremorsense_ft: int = Field(default=0, ge=0)
    blind_beyond_ft: int | None = Field(default=None, ge=0)
    blindsight_requires_hearing: bool = False
