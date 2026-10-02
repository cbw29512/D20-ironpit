from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize
from app.domain.weapons_base import DamageType


class ParryReaction(BaseModel):
    """Standard SRD Parry: add AC against one triggering melee hit while armed."""

    ac_bonus: int = Field(ge=1, le=20)


class RedirectAttackReaction(BaseModel):
    """SRD Goblin Boss reaction: swap with a nearby Small/Medium ally targeted by the same roll."""

    ally_range_ft: int = Field(default=5, ge=1, le=30)
    ally_max_size: CreatureSize = CreatureSize.MEDIUM


class ZeroDamageSaveRedirect(BaseModel):
    """Optional save-damage follow-up after a reduction reaction zeroes an attack."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    resource_id: str = Field(min_length=1)
    resource_cost: int = Field(default=1, ge=1, le=20)
    melee_range_ft: int = Field(default=5, ge=1, le=120)
    ranged_range_ft: int = Field(default=60, ge=1, le=600)
    save_ability: Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    save_dc: int = Field(ge=1, le=40)
    damage_dice_count: int = Field(ge=1, le=20)
    damage_dice_size: int = Field(ge=2, le=100)
    damage_bonus_ability: Literal[
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"
    ] | None = None
    requires_sight: bool = True
    requires_clear_line: bool = True


class AttackDamageReductionReaction(BaseModel):
    """Universal Reaction that reduces damage from one qualifying attack hit."""

    source_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    attack_kinds: list[Literal["melee", "ranged"]] = Field(min_length=1)
    required_damage_types: list[DamageType] = Field(default_factory=list)
    reduction_dice_count: int = Field(default=1, ge=0, le=20)
    reduction_dice_size: int = Field(default=10, ge=2, le=100)
    reduction_ability: Literal[
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"
    ] | None = None
    add_level: bool = False
    zero_damage_redirect: ZeroDamageSaveRedirect | None = None


class DamageReactionAttack(BaseModel):
    """Reusable reaction attack triggered after damage from a nearby creature.

    This is immutable template policy only. Runtime dispatch must separately prove
    that damage was applied, preserve the source creature, check authoritative
    distance, spend the Reaction, and resolve the selected attack immediately.
    """

    source_feature: str = Field(min_length=1)
    trigger: Literal["damaged-by-creature"] = "damaged-by-creature"
    source_range_ft: int = Field(default=5, ge=1, le=120)
    attack_kind: Literal["melee"] = "melee"
