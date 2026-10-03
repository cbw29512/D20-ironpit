from __future__ import annotations

from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, Field, model_validator

from app.domain.combatants import DamageType
from app.domain.debuffs import DebuffCounter
from app.domain.damage_sources import DamageSourceQualifier


class ModifierKind(StrEnum):
    ARMOR_CLASS = "armor-class"
    ARMOR_CLASS_MINIMUM = "armor-class-minimum"
    COVER_ARMOR_CLASS = "cover-armor-class"
    ATTACK_ROLL_FLAT = "attack-roll-flat"
    ATTACK_ROLL_BONUS_DIE = "attack-roll-bonus-die"
    SAVING_THROW_FLAT = "saving-throw-flat"
    COVER_SAVING_THROW_FLAT = "cover-saving-throw-flat"
    SAVING_THROW_BONUS_DIE = "saving-throw-bonus-die"
    SAVING_THROW_ADVANTAGE = "saving-throw-advantage"
    D20_TEST_ADVANTAGE = "d20-test-advantage"
    SAVING_THROW_DISADVANTAGE = "saving-throw-disadvantage"
    DEATH_SAVE_ADVANTAGE = "death-save-advantage"
    HEALING_MAXIMIZE = "healing-maximize"
    CONDITION_IMMUNITY = "condition-immunity"
    ATTACKS_AGAINST_ADVANTAGE = "attacks-against-advantage"
    ATTACKS_AGAINST_DISADVANTAGE = "attacks-against-disadvantage"
    NEXT_ATTACK_AGAINST_ADVANTAGE = "next-attack-against-advantage"
    NEXT_INCOMING_ATTACK_ROLL_FLAT = "next-incoming-attack-roll-flat"
    TARGETING_SAVE_GATE = "targeting-save-gate"
    BONUS_DAMAGE = "bonus-damage"
    SPEED = "speed"
    SPEED_MULTIPLIER = "speed-multiplier"
    DEBUFF_COUNTER = "debuff-counter"
    ZERO_HP_REPLACEMENT = "zero-hp-replacement"
    OPPORTUNITY_ATTACK_SUPPRESSED = "opportunity-attack-suppressed"
    DAMAGE_SOURCE_QUALIFIER = "damage-source-qualifier"
    WEAPON_DAMAGE_TYPE_CHOICE = "weapon-damage-type-choice"
    INVISIBILITY_BENEFITS_SUPPRESSED = "invisibility-benefits-suppressed"


class CombatModifier(BaseModel):
    id: str
    source_id: str
    source_effect_id: str
    source_name: str | None = Field(default=None, min_length=1)
    source_is_magical: bool = False
    kind: ModifierKind
    flat_bonus: int = 0
    multiplier: float = Field(default=1.0, gt=0.0, le=4.0)
    minimum_value: int = Field(default=0, ge=0, le=100)
    dice_count: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(default=0, ge=0, le=100)
    damage_type: DamageType | None = None
    target_id: str | None = None
    weapon_id: str | None = None
    source_qualifier: DamageSourceQualifier | None = None
    condition_id: str | None = None
    debuff_counter: DebuffCounter | None = None
    replacement_hp: int = Field(default=0, ge=0)
    prevents_instant_death: bool = False
    source_creature_types: list[str] = Field(default_factory=list)
    bypass_attacker_senses: list[Literal["blindsight", "truesight"]] = Field(default_factory=list)
    required_active_effect_ids: list[str] = Field(default_factory=list)
    save_ability: str | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    success_immunity_hours: int | None = Field(default=None, ge=1)
    requires_magical_effect: bool = False
    requires_spell_effect: bool = False
    required_effect_tags: list[str] = Field(default_factory=list)
    concentration_required: bool = False
    consume_on_attack_against: bool = False
    consume_on_saving_throw: bool = False
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
        if self.kind is ModifierKind.ARMOR_CLASS_MINIMUM:
            if self.minimum_value < 1 or self.flat_bonus:
                raise ValueError("Minimum AC modifiers require a positive minimum and no flat bonus.")
        elif self.minimum_value:
            raise ValueError(f"{self.kind.value} does not accept a minimum value.")
        damage_type_kinds = {ModifierKind.BONUS_DAMAGE, ModifierKind.WEAPON_DAMAGE_TYPE_CHOICE}
        if self.kind in damage_type_kinds and self.damage_type is None:
            raise ValueError(f"{self.kind.value} requires a damage type.")
        if self.kind not in damage_type_kinds and self.damage_type is not None:
            raise ValueError(f"{self.kind.value} does not accept a damage type.")
        advantage_kinds = {
            ModifierKind.ATTACKS_AGAINST_ADVANTAGE, ModifierKind.ATTACKS_AGAINST_DISADVANTAGE,
            ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE, ModifierKind.D20_TEST_ADVANTAGE,
        }
        if self.kind in advantage_kinds and self.flat_bonus:
            raise ValueError("Attack roll-mode modifiers do not accept a flat bonus.")
        if self.kind is ModifierKind.ATTACK_ROLL_FLAT and (self.flat_bonus == 0 or self.weapon_id is None):
            raise ValueError("Flat attack modifiers require a nonzero bonus and weapon id.")
        if self.kind is ModifierKind.NEXT_INCOMING_ATTACK_ROLL_FLAT and self.flat_bonus == 0:
            raise ValueError("Next incoming attack-roll flat modifiers require a nonzero bonus.")
        weapon_scoped_kinds = {
            ModifierKind.ATTACK_ROLL_FLAT,
            ModifierKind.DAMAGE_SOURCE_QUALIFIER,
            ModifierKind.WEAPON_DAMAGE_TYPE_CHOICE,
        }
        if self.kind not in weapon_scoped_kinds and self.weapon_id is not None:
            raise ValueError(f"{self.kind.value} does not accept a weapon id.")
        if self.kind is ModifierKind.DAMAGE_SOURCE_QUALIFIER and (self.weapon_id is None or self.source_qualifier is None):
            raise ValueError("Damage source qualifier modifiers require a weapon id and qualifier.")
        if self.kind is ModifierKind.WEAPON_DAMAGE_TYPE_CHOICE and self.weapon_id is None:
            raise ValueError("Weapon damage-type choice modifiers require a weapon id.")
        if self.kind is not ModifierKind.DAMAGE_SOURCE_QUALIFIER and self.source_qualifier is not None:
            raise ValueError(f"{self.kind.value} does not accept a source qualifier.")
        if self.kind in {ModifierKind.SAVING_THROW_FLAT, ModifierKind.COVER_SAVING_THROW_FLAT} and self.flat_bonus == 0:
            raise ValueError("Flat saving-throw modifiers require a nonzero bonus.")
        if self.kind is ModifierKind.CONDITION_IMMUNITY and self.condition_id is None:
            raise ValueError("Condition-immunity modifiers require a condition id.")
        if self.kind is not ModifierKind.CONDITION_IMMUNITY and self.condition_id is not None:
            raise ValueError(f"{self.kind.value} does not accept a condition id.")
        if self.kind is ModifierKind.DEBUFF_COUNTER and self.debuff_counter is None:
            raise ValueError("Debuff-counter modifiers require a counter definition.")
        if self.kind is not ModifierKind.DEBUFF_COUNTER and self.debuff_counter is not None:
            raise ValueError(f"{self.kind.value} does not accept a debuff counter.")
        if self.kind is ModifierKind.ZERO_HP_REPLACEMENT and self.replacement_hp < 1:
            raise ValueError("Zero-HP replacement modifiers require positive replacement HP.")
        if self.kind is not ModifierKind.ZERO_HP_REPLACEMENT and (self.replacement_hp or self.prevents_instant_death):
            raise ValueError(f"{self.kind.value} does not accept zero-HP replacement fields.")
        if self.source_creature_types and self.kind not in {
            ModifierKind.ATTACKS_AGAINST_DISADVANTAGE, ModifierKind.CONDITION_IMMUNITY,
            ModifierKind.SAVING_THROW_ADVANTAGE, ModifierKind.TARGETING_SAVE_GATE,
        }:
            raise ValueError(f"{self.kind.value} does not accept source creature types.")
        if self.bypass_attacker_senses and self.kind is not ModifierKind.ATTACKS_AGAINST_DISADVANTAGE:
            raise ValueError(f"{self.kind.value} does not accept attacker-sense bypass.")
        if len(set(self.bypass_attacker_senses)) != len(self.bypass_attacker_senses):
            raise ValueError("Attacker-sense bypass values must be unique.")
        if self.required_active_effect_ids and self.kind is not ModifierKind.CONDITION_IMMUNITY:
            raise ValueError(f"{self.kind.value} does not accept active-effect requirements.")
        required_effects = [item.strip().casefold() for item in self.required_active_effect_ids]
        if any(not item for item in required_effects) or len(set(required_effects)) != len(required_effects):
            raise ValueError("Active-effect requirements must be non-empty and unique.")
        self.required_active_effect_ids = required_effects
        if self.kind in {ModifierKind.SAVING_THROW_ADVANTAGE, ModifierKind.TARGETING_SAVE_GATE} and not self.save_ability:
            raise ValueError(f"{self.kind.value} requires a save ability.")
        if self.kind is ModifierKind.TARGETING_SAVE_GATE and self.save_dc is None:
            raise ValueError("Targeting save gates require a DC.")
        if self.kind is not ModifierKind.TARGETING_SAVE_GATE and self.save_dc is not None:
            raise ValueError(f"{self.kind.value} does not accept a save DC.")
        if self.kind is not ModifierKind.TARGETING_SAVE_GATE and self.success_immunity_hours is not None:
            raise ValueError(f"{self.kind.value} does not accept targeting-gate success immunity.")
        if self.kind not in {
            ModifierKind.SAVING_THROW_ADVANTAGE,
            ModifierKind.SAVING_THROW_FLAT,
            ModifierKind.COVER_SAVING_THROW_FLAT,
            ModifierKind.TARGETING_SAVE_GATE,
        } and self.save_ability:
            raise ValueError(f"{self.kind.value} does not accept a save ability.")
        if self.requires_magical_effect and self.kind is not ModifierKind.SAVING_THROW_ADVANTAGE:
            raise ValueError("Only saving-throw Advantage can require a magical-effect context.")
        if self.requires_spell_effect and self.kind is not ModifierKind.SAVING_THROW_ADVANTAGE:
            raise ValueError("Only saving-throw Advantage can require a spell-effect context.")
        if self.required_effect_tags and self.kind is not ModifierKind.SAVING_THROW_ADVANTAGE:
            raise ValueError("Only saving-throw Advantage can require effect tags.")
        effect_tags = [item.strip().casefold() for item in self.required_effect_tags]
        if any(not item for item in effect_tags) or len(set(effect_tags)) != len(effect_tags):
            raise ValueError("Saving-throw Advantage effect tags must be non-empty and unique.")
        self.required_effect_tags = effect_tags
        if self.consume_on_attack_against and self.kind is not ModifierKind.ATTACKS_AGAINST_ADVANTAGE:
            raise ValueError("Only attack-advantage defender modifiers can be consumed by the next attack.")
        if self.consume_on_saving_throw and self.kind is not ModifierKind.SAVING_THROW_DISADVANTAGE:
            raise ValueError("Only saving-throw Disadvantage modifiers can be consumed by a saving throw.")
        if self.ends_on_owner_attack and self.kind is not ModifierKind.TARGETING_SAVE_GATE:
            raise ValueError("Only targeting save gates can end when their owner attacks.")
        if self.kind is ModifierKind.SPEED and self.flat_bonus == 0:
            raise ValueError("Speed modifiers require a nonzero flat bonus.")
        if self.kind is ModifierKind.SPEED_MULTIPLIER:
            if self.flat_bonus != 0 or self.multiplier == 1.0:
                raise ValueError("Speed multipliers require a non-1 multiplier and no flat bonus.")
        elif self.multiplier != 1.0:
            raise ValueError(f"{self.kind.value} does not accept a multiplier.")
        if self.kind is ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE and self.target_id is None:
            raise ValueError("Target-scoped attack Advantage requires a target id.")
        return self


class ConcentrationState(BaseModel):
    source_id: str
    effect_id: str
    started_round: int = Field(ge=0)
    expires_round: int | None = Field(default=None, ge=1)
    slot_level: int | None = Field(default=None, ge=1, le=9)
