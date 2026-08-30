from __future__ import annotations

import logging

from app.content.monster_equipment import build_monster_visual
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, DamageType, Weapon, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def build_hippogriff() -> CombatantTemplate:
    try:
        rend = WeaponAttack(
            id="hippogriff-rend",
            weapon=Weapon(
                id="hippogriff-rend", name="Rend", attack_kind=WeaponAttackKind.MELEE,
                dice_count=1, dice_size=8, damage_type=DamageType.SLASHING,
                animation="claw", reach_ft=5,
            ),
            attack_bonus=5,
            damage_bonus=3,
        )
        return CombatantTemplate(
            id="srd-hippogriff", name="Hippogriff", archetype="Hippogriff",
            challenge_rating="1", kind="monster", size="large", armor_class=11,
            max_hp=26, speed_ft=60, initiative_bonus=1, weapon_attack=rend,
            attack_action=AttackActionDefinition(
                id="hippogriff-multiattack", name="Multiattack",
                slots=[
                    AttackActionSlot(attack_ids=[rend.id]),
                    AttackActionSlot(attack_ids=[rend.id]),
                ],
            ),
            visual=build_monster_visual("feathers", "claws", "hippogriff"),
            source="SRD 5.2.1 p. 298 Hippogriff",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Hippogriff.")
        raise RuntimeError("Hippogriff could not be created.") from exc
