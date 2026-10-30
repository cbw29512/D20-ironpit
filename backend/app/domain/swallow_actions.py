"""Source-driven Swallow capability shared by 2014 monsters."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.size import CreatureSize


class GrappleSwallowAction(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_name: str = Field(min_length=1)
    attack_id: str = Field(min_length=1)
    delivery_mode: Literal["action_attack", "attack_hit"] = "action_attack"
    max_target_size: CreatureSize
    requires_existing_grapple: bool = True
    damage_dice_count: int = Field(ge=1)
    damage_dice_size: int = Field(ge=2)
    damage_type: str = Field(min_length=1)
    max_swallowed: int | None = Field(default=None, ge=1)
    exit_movement_ft: int = Field(ge=0)
    regurgitation_damage_threshold: int | None = Field(default=None, ge=1)
    regurgitation_save_ability: str | None = None
    regurgitation_save_dc: int | None = Field(default=None, ge=1)
    regurgitation_range_ft: int | None = Field(default=None, ge=0)
    regurgitation_all_swallowed: bool = False
    blinds_and_restrains: bool = True
    grants_total_external_cover: bool = True


def swallow_action_from_source(source) -> GrappleSwallowAction | None:
    if source is None:
        return None
    return GrappleSwallowAction(
        source_name=source.source_name,
        attack_id=source.attack_id,
        delivery_mode=source.delivery_mode,
        max_target_size=source.max_target_size,
        damage_dice_count=source.damage_dice_count,
        damage_dice_size=source.damage_dice_size,
        damage_type=source.damage_type,
        max_swallowed=source.max_swallowed,
        exit_movement_ft=source.exit_movement_ft,
        regurgitation_damage_threshold=source.regurgitation_damage_threshold,
        regurgitation_save_ability=source.regurgitation_save_ability,
        regurgitation_save_dc=source.regurgitation_save_dc,
        regurgitation_range_ft=source.regurgitation_range_ft,
        regurgitation_all_swallowed=source.regurgitation_all_swallowed,
    )
