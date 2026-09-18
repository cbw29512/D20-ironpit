from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from app.domain.combatants import DamageType


class ModifierKind(StrEnum):
    ARMOR_CLASS = "armor-class"
    ATTACK_ROLL_FLAT = "attack-roll-flat"
    ATTACK_ROLL_BONUS_DIE = "attack-roll-bonus-die"
    SAVING_THROW_FLAT = "saving-throw-flat"
    SAVING_THROW_BONUS_DIE = "saving-throw-bonus-die"
    SAVING_THROW_ADVANTAGE = "saving-throw-advantage"
    DEATH_SAVE_ADVANTAGE = "death-save-advantage"
    HEALING_MAXIMIZE = "healing-maximize"
    CONDITION_IMMUNITY = "condition-immunity"
    ATTACKS_AGAINST_ADVANTAGE = "attacks-against-advantage"
    ATTACKS_AGAINST_DISADVANTAGE = "attacks-against-disadvantage"
    NEXT_ATTACK_AGAINST_ADVANTAGE = "next-attack-against-advantage"
    TARGETING_SAVE_GATE = "targeting-save-gate"
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
    weapon_id: str | None = None
    condition_id: str | None = None
    source_creature_types: list[str] = Field(default_factory=list)
    save_ability: str | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    concentration_required: bool = False
    consume_on_attack_against: bool = False
    ends_on_owner_attack: bool = False
    expires_at_start_of_source_turn: bool = False
    expires_at_end_of_target_turn: bool = False
    expires_source_turn_end_round: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_payload(self) -> "CombatModifier":
        die_kind = self.kind in {
            ModifierKind.ATTACK_ROLL_BONUS_DIE, ModifierKind.SAVING_THROW_BONUS_DIE,
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
        advantage_kinds = {
            ModifierKind.ATTACKS_AGAINST_ADVANTAGE, ModifierKind.ATTACKS_AGAINST_DISADVANTAGE,
            ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE,
        }
        if self.kind in advantage_kinds and self.flat_bonus:
            raise ValueError("Attack roll-mode modifiers do not accept a flat bonus.")
        if self.kind is ModifierKind.ATTACK_ROLL_FLAT and (self.flat_bonus == 0 or self.weapon_id is None):
            raise ValueError("Flat attack modifiers require a nonzero bonus and weapon id.")
        if self.kind is not ModifierKind.ATTACK_ROLL_FLAT and self.weapon_id is not None:
            raise ValueError(f"{self.kind.value} does not accept a weapon id.")
        if self.kind is ModifierKind.SAVING_THROW_FLAT and self.flat_bonus == 0:
            raise ValueError("Flat saving-throw modifiers require a nonzero bonus.")
        if self.kind is ModifierKind.CONDITION_IMMUNITY and self.condition_id is None:
            raise ValueError("Condition-immunity modifiers require a condition id.")
        if self.kind is not ModifierKind.CONDITION_IMMUNITY and self.condition_id is not None:
            raise ValueError(f"{self.kind.value} does not accept a condition id.")
        if self.kind is ModifierKind.ATTACKS_AGAINST_DISADVANTAGE and not self.source_creature_types:
            raise ValueError("Typed attack Disadvantage requires source creature types.")
        if self.source_creature_types and self.kind not in {
            ModifierKind.ATTACKS_AGAINST_DISADVANTAGE, ModifierKind.CONDITION_IMMUNITY,
        }:
            raise ValueError(f"{self.kind.value} does not accept source creature types.")
        if self.kind in {ModifierKind.SAVING_THROW_ADVANTAGE, ModifierKind.TARGETING_SAVE_GATE} and not self.save_ability:
            raise ValueError(f"{self.kind.value} requires a save ability.")
        if self.kind is ModifierKind.TARGETING_SAVE_GATE and self.save_dc is None:
            raise ValueError("Targeting save gates require a DC.")
        if self.kind is not ModifierKind.TARGETING_SAVE_GATE and self.save_dc is not None:
            raise ValueError(f"{self.kind.value} does not accept a save DC.")
        if self.kind not in {ModifierKind.SAVING_THROW_ADVANTAGE, ModifierKind.TARGETING_SAVE_GATE} and self.save_ability:
            raise ValueError(f"{self.kind.value} does not accept a save ability.")
        if self.consume_on_attack_against and self.kind is not ModifierKind.ATTACKS_AGAINST_ADVANTAGE:
            raise ValueError("Only attack-advantage defender modifiers can be consumed by the next attack.")
        if self.ends_on_owner_attack and self.kind is not ModifierKind.TARGETING_SAVE_GATE:
            raise ValueError("Only targeting save gates can end when their owner attacks.")
        if self.kind is ModifierKind.SPEED and self.flat_bonus == 0:
            raise ValueError("Speed modifiers require a nonzero flat bonus.")
        if self.kind is ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE and self.target_id is None:
            raise ValueError("Target-scoped attack Advantage requires a target id.")
        return self


class ConcentrationState(BaseModel):
    source_id: str
    effect_id: str
    started_round: int = Field(ge=0)
    expires_round: int | None = Field(default=None, ge=1)
