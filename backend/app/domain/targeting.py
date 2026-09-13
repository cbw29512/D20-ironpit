from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

AreaShape = Literal["radius", "cone", "line", "emanation"]
AreaOrigin = Literal["point", "self"]


class AreaTargeting(BaseModel):
    """Immutable geometry for an action that affects occupied battlefield squares."""

    shape: AreaShape
    origin: AreaOrigin
    radius_ft: int | None = Field(default=None, ge=5)
    length_ft: int | None = Field(default=None, ge=5)
    width_ft: int | None = Field(default=None, ge=5)

    @model_validator(mode="after")
    def validate_shape(self) -> "AreaTargeting":
        values = [value for value in (self.radius_ft, self.length_ft, self.width_ft) if value is not None]
        if any(value % 5 for value in values):
            raise ValueError("Iron Pit area dimensions must use 5-foot increments.")
        if self.shape == "radius":
            if self.origin != "point" or self.radius_ft is None or self.length_ft is not None or self.width_ft is not None:
                raise ValueError("Radius areas require a point origin and only radius_ft.")
        elif self.shape == "emanation":
            if self.origin != "self" or self.radius_ft is None or self.length_ft is not None or self.width_ft is not None:
                raise ValueError("Emanations require a self origin and only radius_ft.")
        elif self.shape == "cone":
            if self.origin != "self" or self.length_ft is None or self.radius_ft is not None or self.width_ft is not None:
                raise ValueError("Cones require a self origin and only length_ft.")
        elif self.shape == "line":
            if self.origin != "self" or self.length_ft is None or self.width_ft is None or self.radius_ft is not None:
                raise ValueError("Lines require self origin, length_ft, and width_ft.")
        return self
