"""Source-driven Swallow capability shared by 2014 monsters."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.domain.size import CreatureSize


class GrappleSwallowAction(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_name: str = Field(min_length=1)
    attack_id: str = Field(min_length=1)
    max_target_size: CreatureSize
    requires_existing_grapple: bool = True
    damage_dice_count: int = Field(ge=1)
    damage_dice_size: int = Field(ge=2)
    damage_type: str = Field(min_length=1)
    max_swallowed: int = Field(ge=1)
    exit_movement_ft: int = Field(ge=0)
    blinds_and_restrains: bool = True
    grants_total_external_cover: bool = True


def swallow_action_from_source(source) -> GrappleSwallowAction | None:
    if source is None:
        return None
    return GrappleSwallowAction(
        source_name=source.source_name,
        attack_id=source.attack_id,
        max_target_size=source.max_target_size,
        damage_dice_count=source.damage_dice_count,
        damage_dice_size=source.damage_dice_size,
        damage_type=source.damage_type,
        max_swallowed=source.max_swallowed,
        exit_movement_ft=source.exit_movement_ft,
    )
