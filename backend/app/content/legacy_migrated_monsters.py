from __future__ import annotations

import logging

from app.content.monster_equipment import build_monster_visual
from app.content.monster_wolf_attacks import build_dire_wolf_bite, build_wolf_bite
from app.domain.models import (
    AttackActionDefinition,
    AttackActionSlot,
    CombatantTemplate,
    DamageType,
    SavingThrowAction,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def build_legacy_wolf() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-wolf", name="Wolf", archetype="Wolf", challenge_rating="1/4",
            kind="monster", ruleset="2024", size=CreatureSize.MEDIUM,
            armor_class=12, max_hp=11, speed_ft=40, initiative_bonus=2,
            weapon_attack=build_wolf_bite(), combat_traits=[CombatTrait.PACK_TACTICS],
            visual=build_monster_visual("fur", "bite", "wolf"),
            source="SRD 5.2.1 Wolf p. 364",
        )
    except Exception as exc:
        logger.exception("Failed to build legacy Wolf migration source.")
        raise RuntimeError("Legacy Wolf migration source could not be built.") from exc


def build_legacy_dire_wolf() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-dire-wolf", name="Dire Wolf", archetype="Dire Wolf", challenge_rating="1",
            kind="monster", ruleset="2024", size=CreatureSize.LARGE,
            armor_class=14, max_hp=22, speed_ft=50, initiative_bonus=2,
            weapon_attack=build_dire_wolf_bite(), combat_traits=[CombatTrait.PACK_TACTICS],
            visual=build_monster_visual("fur", "bite", "dire-wolf"),
            source="SRD 5.2.1 Dire Wolf p. 347",
        )
    except Exception as exc:
        logger.exception("Failed to build legacy Dire Wolf migration source.")
        raise RuntimeError("Legacy Dire Wolf migration source could not be built.") from exc


def build_legacy_giant_constrictor_snake() -> CombatantTemplate:
    try:
        bite = WeaponAttack(
            id="giant-constrictor-snake-bite",
            weapon=Weapon(
                id="giant-constrictor-snake-bite", name="Bite", attack_kind=WeaponAttackKind.MELEE,
                dice_count=2, dice_size=6, damage_type=DamageType.PIERCING,
                animation="bite", reach_ft=10,
            ),
            attack_bonus=6, damage_bonus=4,
        )
        constrict = SavingThrowAction(
            id="giant-constrictor-snake-constrict", name="Constrict", save_ability="strength",
            dc=14, range_ft=10, target_max_size=CreatureSize.LARGE,
            damage_dice_count=2, damage_dice_size=8, damage_bonus=4,
            damage_type="bludgeoning", success_damage="none", grapple_escape_dc=14,
            animation="constrict",
        )
        return CombatantTemplate(
            id="srd-giant-constrictor-snake", name="Giant Constrictor Snake",
            archetype="Giant Constrictor Snake", challenge_rating="2", kind="monster",
            ruleset="2024", size=CreatureSize.HUGE, armor_class=12, max_hp=60,
            speed_ft=30, initiative_bonus=2, weapon_attack=bite,
            attack_action=AttackActionDefinition(
                id="giant-constrictor-snake-multiattack", name="Multiattack",
                slots=[
                    AttackActionSlot(attack_ids=[bite.id]),
                    AttackActionSlot(save_action_ids=[constrict.id]),
                ],
            ),
            saving_throw_actions=[constrict],
            saving_throw_bonuses={
                "strength": 4, "dexterity": 2, "constitution": 1,
                "intelligence": -5, "wisdom": 0, "charisma": -4,
            },
            skill_bonuses={"athletics": 4, "acrobatics": 2, "perception": 2},
            visual=build_monster_visual("natural", "bite", "giant-constrictor-snake"),
            source="SRD 5.2.1 Giant Constrictor Snake p. 355",
        )
    except Exception as exc:
        logger.exception("Failed to build legacy Giant Constrictor Snake migration source.")
        raise RuntimeError("Legacy Giant Constrictor Snake migration source could not be built.") from exc
