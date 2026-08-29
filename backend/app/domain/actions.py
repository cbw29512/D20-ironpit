from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.size import CreatureSize

AbilityName = Literal["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
ActionCost = Literal["action", "bonus_action", "reaction"]
HealingTargetMode = Literal["self", "ally", "self_or_ally"]
DamageTypeName = Literal[
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
]
ConditionName = Literal[
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned", "prone",
    "restrained", "stunned", "unconscious",
]


class GrappleSource(BaseModel):
    source_id: str
    escape_dc: int = Field(ge=1, le=40)
    range_ft: int = Field(default=5, ge=0)
    restrains: bool = False


class HitControlEffect(BaseModel):
    max_target_size: CreatureSize | None = None
    grapple_escape_dc: int | None = Field(default=None, ge=1, le=40)
    restrains_while_grappled: bool = False
    condition_id: ConditionName | None = None
    expires_at_start_of_source_turn: bool = False


class HealingAction(BaseModel):
    """A printed healing option with its actual action cost and target restrictions."""

    id: str
    name: str
    action_cost: ActionCost
    range_ft: int = Field(default=5, ge=0)
    target_mode: HealingTargetMode = "self_or_ally"
    dice_count: int = Field(default=0, ge=0, le=40)
    dice_size: int = Field(default=6, ge=2, le=100)
    healing_bonus: int = Field(default=0, ge=0)
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=20)
    is_spell: bool = False
    animation: str = "healing"


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
    """One ordered Multiattack step; listed weapon/save IDs are legal choices for that step."""

    attack_ids: list[str] = Field(default_factory=list, max_length=16)
    save_action_ids: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def require_choice(self) -> "AttackActionSlot":
        if not self.attack_ids and not self.save_action_ids:
            raise ValueError("Multiattack slot must contain a weapon attack or saving-throw action.")
        return self


class AttackActionDefinition(BaseModel):
    """The ordered strikes/effects a combatant resolves when it uses Multiattack."""

    id: str
    name: str
    slots: list[AttackActionSlot] = Field(min_length=2, max_length=8)
