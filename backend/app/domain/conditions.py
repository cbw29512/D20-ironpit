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


class ConditionExpiry(StrEnum):
    SOURCE_TURN_START = "source_turn_start"
    SOURCE_TURN_END = "source_turn_end"
    TARGET_TURN_START = "target_turn_start"
    TARGET_TURN_END = "target_turn_end"


class ConditionState(BaseModel):
    condition: ConditionType
    source_id: str | None = None
    source_name: str | None = None
    escape_dc: int | None = None
    expires_on: ConditionExpiry | None = None
