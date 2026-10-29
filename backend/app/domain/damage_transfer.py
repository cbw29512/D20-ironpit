from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class DamageTransferRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_name: str
    relation: Literal["source_grapples_target"] = "source_grapples_target"
    source_rounding: Literal["down"] = "down"
    transferred_damage_retriggers: bool = False
