"""Immutable ordered slots or complete source alternatives; no fight state."""
from __future__ import annotations
import logging
from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator
from app.domain.weapons_base import WeaponAttackKind
logger = logging.getLogger(__name__)


class PreviousAttackRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hit: StrictBool = False
    same_target: StrictBool = False

    @model_validator(mode="after")
    def require_constraint(self):
        try:
            if not self.hit and not self.same_target:
                raise ValueError("Previous-attack requirement needs a hit or target constraint.")
            return self
        except Exception:
            logger.exception("Invalid empty previous-attack requirement.")
            raise


class AttackActionSlot(BaseModel):
    previous_attack: PreviousAttackRequirement | None = None
    attack_ids: list[str] = Field(default_factory=list, max_length=16)
    save_action_ids: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def require_choice(self) -> "AttackActionSlot":
        try:
            if not self.attack_ids and not self.save_action_ids:
                raise ValueError("Attack-action slot requires an attack or save action.")
            return self
        except Exception:
            logger.exception("Invalid empty attack-action slot.")
            raise


class AttackActionVariant(BaseModel):
    id: str
    attack_kind: WeaponAttackKind | None = None
    slots: list[AttackActionSlot] = Field(min_length=1, max_length=8)


class AttackActionDefinition(BaseModel):
    id: str
    name: str
    slots: list[AttackActionSlot] = Field(default_factory=list, max_length=8)
    variants: list[AttackActionVariant] = Field(default_factory=list, max_length=16)
    is_attack_action: bool = False

    @model_validator(mode="after")
    def validate_sequences(self) -> "AttackActionDefinition":
        try:
            if bool(self.slots) == bool(self.variants):
                raise ValueError("Attack action requires either slots or complete variants.")
            if len({v.id for v in self.variants}) != len(self.variants):
                raise ValueError("Attack-action variant IDs must be unique.")
            for sequence in ([self.slots] if self.slots else [v.slots for v in self.variants]):
                for index, slot in enumerate(sequence):
                    if slot.previous_attack and (index == 0 or not slot.attack_ids or slot.save_action_ids
                            or not sequence[index-1].attack_ids or sequence[index-1].save_action_ids):
                        raise ValueError("Previous-attack slots require an immediately preceding attack-only slot.")
            return self
        except Exception:
            logger.exception("Invalid attack-action sequences for %s.", self.id)
            raise


def all_action_slots(definition: AttackActionDefinition) -> list[AttackActionSlot]:
    """Reference/range inventory only: resolution must select ONE complete sequence."""
    try:
        return definition.slots or [slot for variant in definition.variants for slot in variant.slots]
    except Exception:
        logger.exception("Failed attack-action slot inventory for %s.", definition.id)
        raise
