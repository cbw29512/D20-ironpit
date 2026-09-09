from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, Field

from app.domain.weapons import WeaponAttackKind


class ConditionAppliedTriggerIR(BaseModel):
    kind: Literal["condition_applied"] = "condition_applied"
    subject: Literal["self", "ally"]


class HitByAttackTriggerIR(BaseModel):
    kind: Literal["hit_by_attack"] = "hit_by_attack"
    attack_kind: WeaponAttackKind | None = None
    requires_weapon_held: bool = False


class TargetedByAttackTriggerIR(BaseModel):
    kind: Literal["targeted_by_attack"] = "targeted_by_attack"
    requires_vision: bool = False


ReactionTriggerIR: TypeAlias = Annotated[
    ConditionAppliedTriggerIR | HitByAttackTriggerIR | TargetedByAttackTriggerIR,
    Field(discriminator="kind"),
]
