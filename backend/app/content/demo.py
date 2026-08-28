from __future__ import annotations

import logging

from app.content.attacks import (
    build_fighter_handaxe_throw,
    build_fighter_longsword_attack,
    build_goblin_scimitar_attack,
    build_goblin_shortbow_attack,
)
from app.content.equipment import build_fighter_visual_loadout, build_goblin_visual_loadout
from app.domain.models import AbilityKind, CombatantTemplate, ResourceDefinition

logger = logging.getLogger(__name__)


def build_demo_fighter() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="aldric-vane-l1",
            name="Aldric Vane",
            archetype="Fighter",
            level=1,
            kind="character",
            armor_class=19,
            max_hp=12,
            speed_ft=30,
            initiative_bonus=1,
            proficiency_bonus=2,
            ability_modifiers={
                AbilityKind.STRENGTH: 3,
                AbilityKind.DEXTERITY: 1,
                AbilityKind.CONSTITUTION: 2,
                AbilityKind.INTELLIGENCE: 0,
                AbilityKind.WISDOM: 2,
                AbilityKind.CHARISMA: -1,
            },
            saving_throw_proficiencies={
                AbilityKind.STRENGTH,
                AbilityKind.CONSTITUTION,
            },
            weapon_attack=build_fighter_longsword_attack(),
            alternate_weapon_attacks=[build_fighter_handaxe_throw()],
            fighting_style="defense",
            weapon_masteries=["longsword", "javelin", "handaxe"],
            visual=build_fighter_visual_loadout(),
            resources=[
                ResourceDefinition(id="second-wind", name="Second Wind", max_uses=2),
            ],
            source="Original level-1 Fighter combat pregen using SRD 5.2.1 rules",
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
            armor_class=15,
            max_hp=10,
            speed_ft=30,
            initiative_bonus=2,
            proficiency_bonus=2,
            ability_modifiers={
                AbilityKind.STRENGTH: -1,
                AbilityKind.DEXTERITY: 2,
                AbilityKind.CONSTITUTION: 0,
                AbilityKind.INTELLIGENCE: 0,
                AbilityKind.WISDOM: -1,
                AbilityKind.CHARISMA: -1,
            },
            weapon_attack=build_goblin_scimitar_attack(),
            alternate_weapon_attacks=[build_goblin_shortbow_attack()],
            bonus_action_features=["nimble-escape"],
            skill_bonuses={"stealth": 6},
            passive_perception=9,
            visual=build_goblin_visual_loadout(),
            source="SRD 5.2.1 Goblin Warrior",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD goblin warrior.")
        raise RuntimeError("Goblin Warrior could not be created.") from exc
