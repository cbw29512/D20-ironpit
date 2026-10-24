from __future__ import annotations

from app.domain.attack_action_definitions import AttackActionDefinition, AttackActionSlot
from app.domain.capability_attack_definitions import (
    AttackCapabilityDefinition,
    ChargeDamageDefinition,
    ChargeProfileDefinition,
)
from app.domain.capability_save_definitions import SaveCapabilityDefinition

CapabilityActionSlot = AttackActionSlot


class MultiattackCapabilityDefinition(AttackActionDefinition):
    name: str = "Multiattack"
