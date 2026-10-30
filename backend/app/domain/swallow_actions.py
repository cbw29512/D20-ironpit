"""Source-driven Swallow capability shared by 2014 monsters.

Simple death-exit profile (Giant Frog/Toad) uses the base fields.
Damage-threshold regurgitation (Behir, Remorhaz, etc.) supplies optional
source-owned threshold, Con-save DC and prone exit distance.
Runtime damage tracking and end-turn save remain a shared primitive to implement;
do not dispatch on names.
"""
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
    # Optional regurgitation profile; None = simple death-exit only
    damage_threshold: int | None = None
    regurgitation_save_ability: str | None = None
    regurgitation_save_dc: int | None = None
    regurgitation_exit_ft: int | None = None
    regurgitation_prone: bool = False


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
        damage_threshold=getattr(source, "damage_threshold", None),
        regurgitation_save_ability=getattr(source, "regurgitation_save_ability", None),
        regurgitation_save_dc=getattr(source, "regurgitation_save_dc", None),
        regurgitation_exit_ft=getattr(source, "regurgitation_exit_ft", None),
        regurgitation_prone=getattr(source, "regurgitation_prone", False),
    )
