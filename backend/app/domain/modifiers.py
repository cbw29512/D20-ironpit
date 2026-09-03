from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from app.domain.combatants import DamageType


class ModifierKind(StrEnum):
    ARMOR_CLASS = "armor-class"
    ATTACK_ROLL_BONUS_DIE = "attack-roll-bonus-die"
    SAVING_THROW_BONUS_DIE = "saving-throw-bonus-die"
    ATTACKS_AGAINST_ADVANTAGE = "attacks-against-advantage"
    NEXT_ATTACK_AGAINST_ADVANTAGE = "next-attack-against-advantage"
    BONUS_DAMAGE = "bonus-damage"
    SPEED = "speed"


class CombatModifier(BaseModel):
    id: str
    source_id: str
    source_effect_id: str
    kind: ModifierKind
    flat_bonus: int = 0
    dice_count: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(default=0, ge=0, le=100)
    damage_type: DamageType | None = None
    target_id: str | None = None
    concentration_required: bool = False
    consume_on_attack_against: bool = False
    expires_at_start_of_source_turn: bool = False
    expires_at_end_of_target_turn: bool = False
    expires_source_turn_end_round: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_payload(self) -> "CombatModifier":
        die_kind = self.kind in {
            ModifierKind.ATTACK_ROLL_BONUS_DIE,
            ModifierKind.SAVING_THROW_BONUS_DIE,
            ModifierKind.BONUS_DAMAGE,
        }
        if die_kind and (self.dice_count < 1 or self.dice_size < 2):
            raise ValueError(f"{self.kind.value} requires certified dice.")
        if not die_kind and (self.dice_count or self.dice_size):
            raise ValueError(f"{self.kind.value} does not accept dice.")
        if self.kind is ModifierKind.BONUS_DAMAGE and self.damage_type is None:
            raise ValueError("Bonus damage requires a damage type.")
        if self.kind is not ModifierKind.BONUS_DAMAGE and self.damage_type is not None:
            raise ValueError(f"{self.kind.value} does not accept a damage type.")
        advantage_kinds = {ModifierKind.ATTACKS_AGAINST_ADVANTAGE, ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE}
        if self.kind in advantage_kinds and self.flat_bonus:
            raise ValueError("Attack-advantage modifiers do not accept a flat bonus.")
        if self.kind is ModifierKind.SPEED and self.flat_bonus == 0:
            raise ValueError("Speed modifiers require a nonzero flat bonus.")
        if self.kind is ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE and self.target_id is None:
            raise ValueError("Target-scoped attack Advantage requires a target id.")
        if self.consume_on_attack_against and self.kind is not ModifierKind.ATTACKS_AGAINST_ADVANTAGE:
            raise ValueError("Only attack-advantage defender modifiers can use consume_on_attack_against.")
        return self


class ConcentrationState(BaseModel):
    source_id: str
    effect_id: str
    started_round: int = Field(ge=0)
    expires_round: int | None = Field(default=None, ge=1)
