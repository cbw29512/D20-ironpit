from __future__ import annotations

import logging

from app.content.attacks import (
    build_fighter_longsword_attack,
    build_goblin_scimitar_attack,
    build_goblin_shortbow_attack,
)
from app.content.equipment import build_fighter_visual_loadout, build_goblin_visual_loadout
from app.domain.models import CombatantTemplate, ResourceDefinition

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
            weapon_attack=build_fighter_longsword_attack(),
            saving_throw_bonuses={
                "strength": 5, "dexterity": 1, "constitution": 4,
                "intelligence": 0, "wisdom": 1, "charisma": -1,
            },
            skill_bonuses={"athletics": 5, "acrobatics": 1},
            fighting_style="Defense",
            weapon_masteries=["greataxe", "greatsword", "halberd"],
            visual=build_fighter_visual_loadout(),
            resources=[
                ResourceDefinition(id="second-wind", name="Second Wind", max_uses=2),
            ],
            source="Original pregen built from SRD 5.2.1 Fighter level 1 rules",
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
            size="small",
            armor_class=15,
            max_hp=10,
            speed_ft=30,
            initiative_bonus=2,
            weapon_attack=build_goblin_scimitar_attack(),
            alternate_weapon_attacks=[build_goblin_shortbow_attack()],
            visual=build_goblin_visual_loadout(),
            source="SRD 5.2.1 Goblin Warrior",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD goblin warrior.")
        raise RuntimeError("Goblin Warrior could not be created.") from exc
