from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

AreaShape = Literal["cone", "line", "emanation", "sphere", "cylinder"]


class AreaTargeting(BaseModel):
    """Printed area geometry; resolver behavior is source-name independent."""

    shape: AreaShape
    length_ft: int | None = Field(default=None, ge=5)
    width_ft: int | None = Field(default=None, ge=5)
    radius_ft: int | None = Field(default=None, ge=5)
    height_ft: int | None = Field(default=None, ge=5)
    origin_range_ft: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_shape_dimensions(self) -> "AreaTargeting":
        values = (self.length_ft, self.width_ft, self.radius_ft, self.height_ft)
        if any(value is not None and value % 5 for value in values):
            raise ValueError("Iron Pit area dimensions must use 5-foot increments.")
        if self.shape == "cone":
            if self.length_ft is None or any(value is not None for value in (self.width_ft, self.radius_ft, self.height_ft)):
                raise ValueError("Cone requires only length_ft.")
        elif self.shape == "line":
            if self.length_ft is None or self.width_ft is None or any(value is not None for value in (self.radius_ft, self.height_ft)):
                raise ValueError("Line requires length_ft and width_ft.")
        elif self.shape == "emanation":
            if self.radius_ft is None or any(value is not None for value in (self.length_ft, self.width_ft, self.height_ft)):
                raise ValueError("Emanation requires only radius_ft.")
            if self.origin_range_ft != 0:
                raise ValueError("Emanation originates from its source.")
        elif self.shape == "sphere":
            if self.radius_ft is None or any(value is not None for value in (self.length_ft, self.width_ft, self.height_ft)):
                raise ValueError("Sphere requires only radius_ft.")
        elif self.shape == "cylinder":
            if self.radius_ft is None or self.height_ft is None or any(value is not None for value in (self.length_ft, self.width_ft)):
                raise ValueError("Cylinder requires radius_ft and height_ft.")
        return self
