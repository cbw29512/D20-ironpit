from __future__ import annotations

import logging

from app.domain.models import (
    AttackActionDefinition,
    AttackActionSlot,
    CombatantTemplate,
    DamageType,
    HitControlEffect,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _attack(
    attack_id: str, name: str, dice_count: int, dice_size: int,
    damage_type: DamageType, reach_ft: int,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id, name=name, attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count, dice_size=dice_size, damage_type=damage_type,
            animation="bite" if name == "Bite" else "heavy-strike", reach_ft=reach_ft,
        ),
        attack_bonus=10,
        damage_bonus=7,
    )


def build_tyrannosaurus_rex() -> CombatantTemplate:
    try:
        bite = _attack("tyrannosaurus-rex-bite", "Bite", 4, 12, DamageType.PIERCING, 10)
        bite = bite.model_copy(update={
            "control_effect": HitControlEffect(
                max_target_size=CreatureSize.LARGE,
                grapple_escape_dc=17,
                restrains_while_grappled=True,
            ),
        })
        tail = _attack("tyrannosaurus-rex-tail", "Tail", 4, 8, DamageType.BLUDGEONING, 15)
        tail = tail.model_copy(update={
            "knocks_prone_max_size": CreatureSize.HUGE,
            "forbid_target_grappled_by_self": True,
        })
        return CombatantTemplate(
            id="srd-tyrannosaurus-rex",
            name="Tyrannosaurus Rex",
            archetype="Tyrannosaurus Rex",
            challenge_rating="8",
            kind="monster",
            size=CreatureSize.HUGE,
            armor_class=13,
            max_hp=136,
            speed_ft=50,
            initiative_bonus=3,
            weapon_attack=bite,
            alternate_weapon_attacks=[tail],
            attack_action=AttackActionDefinition(
                id="tyrannosaurus-rex-multiattack",
                name="Multiattack",
                slots=[
                    AttackActionSlot(attack_ids=[bite.id]),
                    AttackActionSlot(attack_ids=[tail.id]),
                ],
            ),
            saving_throw_bonuses={
                "strength": 10, "dexterity": 0, "constitution": 4,
                "intelligence": -4, "wisdom": 4, "charisma": -1,
            },
            skill_bonuses={"perception": 4},
            visual=VisualLoadout(
                armor="natural", main_hand="jaws", body_style="tyrannosaurus",
            ),
            source="SRD 5.2.1 Tyrannosaurus Rex p. 363",
        )
    except Exception as exc:
        logger.exception("Failed to build Tyrannosaurus Rex combat template.")
        raise RuntimeError("Tyrannosaurus Rex template could not be created.") from exc
