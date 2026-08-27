from __future__ import annotations

import logging

from app.content.attacks import (
    build_fighter_longsword_attack,
    build_goblin_scimitar_attack,
    build_goblin_shortbow_attack,
)
from app.content.equipment import build_fighter_visual_loadout, build_goblin_visual_loadout
from app.domain.models import (
    Ability,
    CombatantTemplate,
    CreatureType,
    ResourceDefinition,
    SizeCategory,
    Skill,
)

logger = logging.getLogger(__name__)


def build_demo_fighter() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="aldric-vane-l1",
            name="Aldric Vane",
            archetype="Fighter",
            level=1,
            kind="character",
            creature_type=CreatureType.HUMANOID,
            size=SizeCategory.MEDIUM,
            armor_class=18,
            max_hp=12,
            speed_ft=30,
            initiative_bonus=1,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 3,
                Ability.DEXTERITY: 1,
                Ability.CONSTITUTION: 2,
                Ability.INTELLIGENCE: 0,
                Ability.WISDOM: 0,
                Ability.CHARISMA: 0,
            },
            saving_throw_modifiers={Ability.STRENGTH: 5, Ability.CONSTITUTION: 4},
            skill_modifiers={Skill.ATHLETICS: 5, Skill.ACROBATICS: 1},
            weapon_attack=build_fighter_longsword_attack(),
            visual=build_fighter_visual_loadout(),
            resources=[ResourceDefinition(id="second-wind", name="Second Wind", max_uses=2)],
            source="Original pregen using SRD 5.2.1 rules",
        )
    except Exception as exc:
        logger.exception("Failed to build demo fighter.")
        raise RuntimeError("Demo fighter could not be created.") from exc


def build_goblin_warrior() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-goblin-warrior",
            name="Goblin Warrior",
            archetype="Goblin Warrior",
            challenge_rating="1/4",
            kind="monster",
            creature_type=CreatureType.FEY,
            creature_tags=["goblinoid"],
            size=SizeCategory.SMALL,
            armor_class=15,
            max_hp=10,
            speed_ft=30,
            initiative_bonus=2,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: -1,
                Ability.DEXTERITY: 2,
                Ability.CONSTITUTION: 0,
                Ability.INTELLIGENCE: 0,
                Ability.WISDOM: -1,
                Ability.CHARISMA: -1,
            },
            weapon_attack=build_goblin_scimitar_attack(),
            alternate_weapon_attacks=[build_goblin_shortbow_attack()],
            visual=build_goblin_visual_loadout(),
            source="SRD 5.2.1 Goblin Warrior",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD goblin warrior.")
        raise RuntimeError("Goblin Warrior could not be created.") from exc
