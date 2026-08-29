from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.domain.size import CreatureSize

AbilityName = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
DamageTypeName = Literal[
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
]


class GrappleSource(BaseModel):
    source_id: str
    escape_dc: int = Field(ge=1, le=40)
    restrains: bool = False


class HitControlEffect(BaseModel):
    max_target_size: CreatureSize | None = None
    grapple_escape_dc: int | None = Field(default=None, ge=1, le=40)
    restrains_while_grappled: bool = False


class SavingThrowAction(BaseModel):
    id: str
    name: str
    save_ability: AbilityName
    dc: int = Field(ge=1, le=40)
    range_ft: int = Field(ge=0)
    target_max_size: CreatureSize | None = None
    damage_dice_count: int = Field(default=0, ge=0, le=40)
    damage_dice_size: int = Field(default=6, ge=2, le=100)
    damage_bonus: int = 0
    damage_type: DamageTypeName | None = None
    success_damage: Literal["none", "half"] = "none"
    grapple_escape_dc: int | None = Field(default=None, ge=1, le=40)
    restrains_while_grappled: bool = False
    animation: str = "save-effect"


class AttackActionSlot(BaseModel):
    """One attack granted by an Attack action; listed IDs are legal choices for the slot."""

    attack_ids: list[str] = Field(min_length=1, max_length=16)


class AttackActionDefinition(BaseModel):
    """The attack rolls a combatant can make when it takes its preferred Attack action."""

    id: str
    name: str
    slots: list[AttackActionSlot] = Field(min_length=2, max_length=8)
