from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    AttackActionDefinition,
    AttackActionSlot,
    CombatantTemplate,
    DamageType,
    HitControlEffect,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize


def _attack(
    attack_id: str,
    name: str,
    dice_count: int,
    dice_size: int,
    damage_type: DamageType,
    reach_ft: int,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id,
            name=name,
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count,
            dice_size=dice_size,
            damage_type=damage_type,
            animation="bite" if name == "Bite" else "heavy-strike",
            reach_ft=reach_ft,
        ),
        attack_bonus=8,
        damage_bonus=5,
    )


def build_giant_crocodile() -> CombatantTemplate:
    bite = _attack("giant-crocodile-bite", "Bite", 3, 10, DamageType.PIERCING, 5)
    bite = bite.model_copy(update={
        "control_effect": HitControlEffect(
            max_target_size=CreatureSize.LARGE,
            grapple_escape_dc=15,
            restrains_while_grappled=True,
        ),
    })
    tail = _attack("giant-crocodile-tail", "Tail", 3, 8, DamageType.BLUDGEONING, 10)
    tail = tail.model_copy(update={
        "knocks_prone_max_size": CreatureSize.LARGE,
        "forbid_target_grappled_by_self": True,
    })
    return CombatantTemplate(
        id="srd-giant-crocodile",
        name="Giant Crocodile",
        archetype="Giant Crocodile",
        challenge_rating="5",
        kind="monster",
        size=CreatureSize.HUGE,
        armor_class=14,
        max_hp=85,
        speed_ft=30,
        initiative_bonus=-1,
        weapon_attack=bite,
        alternate_weapon_attacks=[tail],
        attack_action=AttackActionDefinition(
            id="giant-crocodile-multiattack",
            name="Multiattack",
            slots=[AttackActionSlot(attack_ids=[bite.id]), AttackActionSlot(attack_ids=[tail.id])],
        ),
        skill_bonuses={"stealth": 5},
        visual=build_monster_visual("natural", "bite", "giant-crocodile"),
        source="SRD 5.2.1 Giant Crocodile p. 350",
    )
