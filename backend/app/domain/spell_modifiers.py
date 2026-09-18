from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionName, DamageTypeName

SpellModifierKind = Literal[
    "armor-class", "attack-roll-bonus-die", "saving-throw-bonus-die", "saving-throw-advantage",
    "death-save-advantage", "healing-maximize", "condition-immunity", "attacks-against-advantage",
    "attacks-against-disadvantage", "targeting-save-gate", "bonus-damage", "speed",
]


class SpellModifierEffect(BaseModel):
    """Source-neutral modifier data converted to a runtime CombatModifier when a spell resolves."""

    kind: SpellModifierKind
    flat_bonus: int = 0
    dice_count: int = Field(default=0, ge=0, le=20)
    dice_size: int = Field(default=0, ge=0, le=100)
    damage_type: DamageTypeName | None = None
    condition_id: ConditionName | None = None
    source_creature_types: list[str] = Field(default_factory=list)
    save_ability: AbilityName | None = None
    save_dc: int | None = Field(default=None, ge=1, le=40)
    consume_on_attack_against: bool = False
    ends_on_owner_attack: bool = False
    expires_after_source_turns: int | None = Field(default=None, ge=1, le=20)

    @model_validator(mode="after")
    def validate_payload(self) -> "SpellModifierEffect":
        die_kind = self.kind in {"attack-roll-bonus-die", "saving-throw-bonus-die", "bonus-damage"}
        if die_kind and (self.dice_count < 1 or self.dice_size < 2):
            raise ValueError(f"{self.kind} requires certified dice.")
        if not die_kind and (self.dice_count or self.dice_size):
            raise ValueError(f"{self.kind} does not accept dice.")
        if self.kind == "bonus-damage" and self.damage_type is None:
            raise ValueError("Bonus damage requires a damage type.")
        if self.kind != "bonus-damage" and self.damage_type is not None:
            raise ValueError(f"{self.kind} does not accept a damage type.")
        if self.kind == "condition-immunity" and self.condition_id is None:
            raise ValueError("Condition immunity requires a condition id.")
        if self.kind != "condition-immunity" and self.condition_id is not None:
            raise ValueError(f"{self.kind} does not accept a condition id.")
        if self.kind == "attacks-against-disadvantage" and not self.source_creature_types:
            raise ValueError("Typed attack Disadvantage requires source creature types.")
        if self.source_creature_types and self.kind not in {"attacks-against-disadvantage", "condition-immunity"}:
            raise ValueError(f"{self.kind} does not accept source creature types.")
        if self.kind in {"saving-throw-advantage", "targeting-save-gate"} and not self.save_ability:
            raise ValueError(f"{self.kind} requires a save ability.")
        if self.kind == "targeting-save-gate" and self.save_dc is None:
            raise ValueError("Targeting save gates require a DC.")
        if self.kind != "targeting-save-gate" and self.save_dc is not None:
            raise ValueError(f"{self.kind} does not accept a save DC.")
        if self.kind not in {"saving-throw-advantage", "targeting-save-gate"} and self.save_ability:
            raise ValueError(f"{self.kind} does not accept a save ability.")
        if self.consume_on_attack_against and self.kind != "attacks-against-advantage":
            raise ValueError("Only attack-advantage spell modifiers can be consumed by the next attack.")
        if self.ends_on_owner_attack and self.kind != "targeting-save-gate":
            raise ValueError("Only targeting save gates can end when their owner attacks.")
        return self
