from __future__ import annotations

import logging

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    AttackActionDefinition,
    AttackActionSlot,
    CombatantTemplate,
    CombatTrait,
    DamageType,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _attack(
    attack_id: str,
    name: str,
    kind: WeaponAttackKind,
    bonus: int,
    dice_count: int,
    dice_size: int,
    damage_bonus: int,
    damage_type: DamageType,
    *,
    normal: int | None = None,
    long: int | None = None,
    reach: int = 5,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id,
            name=name,
            attack_kind=kind,
            dice_count=dice_count,
            dice_size=dice_size,
            damage_type=damage_type,
            reach_ft=reach if kind is WeaponAttackKind.MELEE else 0,
            normal_range_ft=normal,
            long_range_ft=long,
            animation="projectile" if kind is WeaponAttackKind.RANGED else "heavy-strike",
        ),
        attack_bonus=bonus,
        damage_bonus=damage_bonus,
    )


def _monster(**kwargs) -> CombatantTemplate:
    try:
        return CombatantTemplate(kind="monster", **kwargs)
    except Exception as exc:
        monster_id = kwargs.get("id", "unknown")
        logger.exception("Failed to build batch-three monster %s.", monster_id)
        raise RuntimeError(f"Monster {monster_id} could not be created.") from exc


def build_monster_batch_three() -> list[CombatantTemplate]:
    ogre_club = _attack("ogre-greatclub", "Greatclub", WeaponAttackKind.MELEE, 6, 2, 8, 4, DamageType.BLUDGEONING)
    ogre_javelin_melee = _attack("ogre-javelin-melee", "Javelin", WeaponAttackKind.MELEE, 6, 2, 6, 4, DamageType.PIERCING)
    ogre_javelin = _attack("ogre-javelin", "Javelin", WeaponAttackKind.RANGED, 6, 2, 6, 4, DamageType.PIERCING, normal=30, long=120)
    owlbear_rend = _attack("owlbear-rend", "Rend", WeaponAttackKind.MELEE, 7, 2, 8, 5, DamageType.SLASHING)
    saber_rend = _attack("saber-toothed-tiger-rend", "Rend", WeaponAttackKind.MELEE, 6, 2, 6, 4, DamageType.SLASHING)
    scout_longbow = _attack("scout-longbow", "Longbow", WeaponAttackKind.RANGED, 4, 1, 8, 2, DamageType.PIERCING, normal=150, long=600)
    scout_sword = _attack("scout-shortsword", "Shortsword", WeaponAttackKind.MELEE, 4, 1, 6, 2, DamageType.PIERCING)
    infantry_spear = _attack("warrior-infantry-spear-melee", "Spear", WeaponAttackKind.MELEE, 3, 1, 6, 1, DamageType.PIERCING)
    infantry_throw = _attack("warrior-infantry-spear-ranged", "Spear", WeaponAttackKind.RANGED, 3, 1, 6, 1, DamageType.PIERCING, normal=20, long=60)

    return [
        _monster(
            id="srd-ogre", name="Ogre", archetype="Ogre", challenge_rating="2",
            size=CreatureSize.LARGE, armor_class=11, max_hp=68, speed_ft=40, initiative_bonus=-1,
            weapon_attack=ogre_club, alternate_weapon_attacks=[ogre_javelin_melee, ogre_javelin],
            visual=build_monster_visual("natural", "greatclub", "ogre"), source="SRD 5.2.1 Ogre p. 312",
        ),
        _monster(
            id="srd-owlbear", name="Owlbear", archetype="Owlbear", challenge_rating="3",
            size=CreatureSize.LARGE, armor_class=13, max_hp=59, speed_ft=40, initiative_bonus=1,
            weapon_attack=owlbear_rend,
            attack_action=AttackActionDefinition(id="owlbear-multiattack", name="Multiattack", slots=[AttackActionSlot(attack_ids=[owlbear_rend.id]), AttackActionSlot(attack_ids=[owlbear_rend.id])]),
            visual=build_monster_visual("natural", "rend", "owlbear"), source="SRD 5.2.1 Owlbear p. 313",
        ),
        _monster(
            id="srd-saber-toothed-tiger", name="Saber-Toothed Tiger", archetype="Saber-Toothed Tiger", challenge_rating="2",
            size=CreatureSize.LARGE, armor_class=13, max_hp=52, speed_ft=40, initiative_bonus=3,
            weapon_attack=saber_rend,
            attack_action=AttackActionDefinition(id="saber-toothed-tiger-multiattack", name="Multiattack", slots=[AttackActionSlot(attack_ids=[saber_rend.id]), AttackActionSlot(attack_ids=[saber_rend.id])]),
            visual=build_monster_visual("natural", "rend", "saber-toothed-tiger"), source="SRD 5.2.1 Saber-Toothed Tiger p. 360",
        ),
        _monster(
            id="srd-scout", name="Scout", archetype="Scout", challenge_rating="1/2",
            size=CreatureSize.MEDIUM, armor_class=13, max_hp=16, speed_ft=30, initiative_bonus=2,
            weapon_attack=scout_longbow, alternate_weapon_attacks=[scout_sword],
            attack_action=AttackActionDefinition(id="scout-multiattack", name="Multiattack", slots=[AttackActionSlot(attack_ids=[scout_longbow.id, scout_sword.id]), AttackActionSlot(attack_ids=[scout_longbow.id, scout_sword.id])]),
            visual=build_monster_visual("leather", "longbow", "humanoid"), source="SRD 5.2.1 Scout p. 322",
        ),
        _monster(
            id="srd-warrior-infantry", name="Warrior Infantry", archetype="Warrior Infantry", challenge_rating="1/8",
            size=CreatureSize.MEDIUM, armor_class=13, max_hp=9, speed_ft=30, initiative_bonus=0,
            weapon_attack=infantry_spear, alternate_weapon_attacks=[infantry_throw],
            combat_traits=[CombatTrait.PACK_TACTICS],
            visual=build_monster_visual("chain-shirt", "spear", "humanoid"), source="SRD 5.2.1 Warrior Infantry p. 336",
        ),
    ]
