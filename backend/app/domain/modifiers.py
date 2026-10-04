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
    WEAPON_DAMAGE_FLAT = "weapon-damage-flat"
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
        from app.domain.modifier_validation import validate_combat_modifier_payload

        validate_combat_modifier_payload(self)
        return self


class ConcentrationState(BaseModel):
    source_id: str
    effect_id: str
    started_round: int = Field(ge=0)
    expires_round: int | None = Field(default=None, ge=1)
    slot_level: int | None = Field(default=None, ge=1, le=9)
