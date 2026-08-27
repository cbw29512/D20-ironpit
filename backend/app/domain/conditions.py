from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class ConditionType(StrEnum):
    PRONE = "prone"
    GRAPPLED = "grappled"
    POISONED = "poisoned"
    FRIGHTENED = "frightened"
    RESTRAINED = "restrained"
    PARALYZED = "paralyzed"


class ConditionState(BaseModel):
    condition: ConditionType
    source_id: str | None = None
    source_name: str | None = None
    escape_dc: int | None = None
