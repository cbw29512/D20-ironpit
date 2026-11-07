"""Source-driven Swallow capability shared by 2014 monsters."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
import logging

logger = logging.getLogger(__name__)

from app.domain.size import CreatureSize


class GrappleSwallowAction(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_name: str = Field(min_length=1)
    attack_id: str = Field(min_length=1)
    delivery_mode: Literal["action_attack", "attack_hit", "attack_sequence"] = "action_attack"
    max_target_size: CreatureSize
    requires_existing_grapple: bool = True
    on_hit_save_ability: str | None = None
    on_hit_save_dc: int | None = Field(default=None, ge=1, le=40)
    required_sequence_hits: int = Field(default=0, ge=0, le=8)
    sequence_grapple_dc: int | None = Field(default=None, ge=1, le=40)
    start_turn_save_ability: str | None = None
    start_turn_save_dc: int | None = Field(default=None, ge=1, le=40)
    damage_bonus: int = Field(default=0, ge=0, le=100)
    exit_prone: bool = True
    cannot_breathe: bool = False
    moves_with_source: bool = False
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

    @model_validator(mode="after")
    def validate_initial_hit_save(self) -> "GrappleSwallowAction":
        try:
            if (self.on_hit_save_ability is None) != (self.on_hit_save_dc is None):
                raise ValueError("Swallow initial on-hit saving throw needs ability and DC.")
            if self.on_hit_save_dc is not None and (self.delivery_mode != "attack_hit" or self.requires_existing_grapple):
                raise ValueError("Initial hit-save Swallow must be an attack hit without a prior grapple.")
            if self.delivery_mode == "attack_sequence":
                if (self.required_sequence_hits < 2 or self.sequence_grapple_dc is None
                        or not self.requires_existing_grapple or self.on_hit_save_dc is not None):
                    raise ValueError("Two-hit containment requires a prior printed hit sequence and Grapple DC.")
                if (self.start_turn_save_ability is None) != (self.start_turn_save_dc is None):
                    raise ValueError("Conditional source-turn damage needs saving throw ability and DC.")
                if self.start_turn_save_dc is None or self.max_swallowed is None:
                    raise ValueError("Two-hit containment must declare its source-turn save and capacity.")
            elif self.required_sequence_hits or self.sequence_grapple_dc is not None:
                raise ValueError("Sequence-hit fields belong only to attack-sequence containment.")
            if self.delivery_mode != "attack_sequence" and self.start_turn_save_dc is not None:
                raise ValueError("A distinct source-turn save requires the declared sequence profile.")
            if (not self.requires_existing_grapple and self.on_hit_save_dc is None
                    and self.delivery_mode != "attack_sequence"):
                raise ValueError("Non-grapple Swallow must declare a printed initial saving throw.")
            return self
        except Exception:
            logger.exception("Invalid generic Swallow hit/save contract.")
            raise


def swallow_action_from_source(source) -> GrappleSwallowAction | None:
    if source is None:
        return None
    return GrappleSwallowAction(
        source_name=source.source_name,
        attack_id=source.attack_id,
        delivery_mode=source.delivery_mode,
        requires_existing_grapple=source.requires_existing_grapple,
        on_hit_save_ability=source.on_hit_save_ability,
        on_hit_save_dc=source.on_hit_save_dc,
        required_sequence_hits=source.required_sequence_hits,
        sequence_grapple_dc=source.sequence_grapple_dc,
        start_turn_save_ability=source.start_turn_save_ability,
        start_turn_save_dc=source.start_turn_save_dc,
        damage_bonus=source.damage_bonus,
        exit_prone=source.exit_prone,
        cannot_breathe=source.cannot_breathe,
        moves_with_source=source.moves_with_source,
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
