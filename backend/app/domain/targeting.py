from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

AreaShape = Literal["radius", "cone", "line", "emanation"]
AreaOrigin = Literal["point", "self"]


class AreaTargeting(BaseModel):
    shape: AreaShape
    origin: AreaOrigin
    radius_ft: int | None = Field(default=None, ge=5)
    length_ft: int | None = Field(default=None, ge=5)
    width_ft: int | None = Field(default=None, ge=5)

    @model_validator(mode="after")
    def validate_shape(self) -> "AreaTargeting":
        values = (self.radius_ft, self.length_ft, self.width_ft)
        if any(value is not None and value % 5 for value in values):
            raise ValueError("Area dimensions must use 5-foot increments.")
        if self.shape in {"radius", "emanation"}:
            if self.radius_ft is None or self.length_ft is not None or self.width_ft is not None:
                raise ValueError(f"{self.shape} requires radius_ft only.")
        elif self.shape == "cone":
            if self.length_ft is None or self.radius_ft is not None or self.width_ft is not None:
                raise ValueError("cone requires length_ft only.")
        elif self.length_ft is None or self.width_ft is None or self.radius_ft is not None:
            raise ValueError("line requires length_ft and width_ft.")
        if self.shape in {"cone", "line", "emanation"} and self.origin != "self":
            raise ValueError(f"{self.shape} must originate from self.")
        return self
