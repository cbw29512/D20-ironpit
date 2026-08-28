from __future__ import annotations

import logging

from app.content.thrown_weapons import build_handaxe_throw
from app.domain.models import (
    AbilityKind,
    CombatantTemplate,
    DamageType,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
    WeaponProperty,
)

logger = logging.getLogger(__name__)


def build_greataxe() -> Weapon:
    try:
        return Weapon(
            id="greataxe",
            name="Greataxe",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=12,
            damage_type=DamageType.SLASHING,
            animation="slash",
            reach_ft=5,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery_property="cleave",
        )
    except Exception as exc:
        logger.exception("Failed to build Greataxe.")
        raise RuntimeError("Greataxe could not be created.") from exc


def build_demo_barbarian() -> CombatantTemplate:
    """Classic level-1 Barbarian combat slice using SRD 5.2.1 rules."""
    try:
        greataxe = WeaponAttack(
            id="kara-greataxe",
            weapon=build_greataxe(),
            attack_bonus=5,
            ability=AbilityKind.STRENGTH,
            ability_damage_modifier=3,
        )
        handaxe = WeaponAttack(
            id="kara-handaxe-throw",
            weapon=build_handaxe_throw(),
            attack_bonus=5,
            ability=AbilityKind.STRENGTH,
            ability_damage_modifier=3,
        )
        return CombatantTemplate(
            id="kara-stonefury-l1",
            name="Kara Stonefury",
            archetype="Barbarian",
            level=1,
            kind="character",
            armor_class=15,
            max_hp=15,
            speed_ft=30,
            initiative_bonus=2,
            proficiency_bonus=2,
            ability_modifiers={
                AbilityKind.STRENGTH: 3,
                AbilityKind.DEXTERITY: 2,
                AbilityKind.CONSTITUTION: 3,
                AbilityKind.INTELLIGENCE: -1,
                AbilityKind.WISDOM: 0,
                AbilityKind.CHARISMA: -1,
            },
            saving_throw_proficiencies={AbilityKind.STRENGTH, AbilityKind.CONSTITUTION},
            weapon_attack=greataxe,
            alternate_weapon_attacks=[handaxe],
            weapon_masteries=["greataxe", "handaxe"],
            bonus_action_features=["rage"],
            skill_bonuses={"athletics": 5, "perception": 0},
            passive_perception=10,
            visual=VisualLoadout(
                armor="unarmored",
                main_hand="greataxe",
                off_hand=None,
                body_style="barbarian",
            ),
            resources=[ResourceDefinition(id="rage", name="Rage", max_uses=2)],
            source="Original level-1 pregen using SRD 5.2.1 Barbarian rules and starting Greataxe package",
        )
    except Exception as exc:
        logger.exception("Failed to build demo Barbarian.")
        raise RuntimeError("Demo Barbarian could not be created.") from exc
