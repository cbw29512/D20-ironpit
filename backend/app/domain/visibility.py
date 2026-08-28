from enum import StrEnum

from pydantic import BaseModel


class CoverLevel(StrEnum):
    NONE = "none"
    HALF = "half"
    THREE_QUARTERS = "three-quarters"
    TOTAL = "total"


class ActorVisibilityState(BaseModel):
    heavily_obscured: bool = False
    cover: CoverLevel = CoverLevel.NONE
    enemy_line_of_sight: bool = True
