from __future__ import annotations

from pydantic import BaseModel, Field


class ResourceState(BaseModel):
    id: str
    name: str
    current_uses: int = Field(ge=0)
    max_uses: int = Field(ge=0)
