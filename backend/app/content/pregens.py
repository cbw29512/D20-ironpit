from __future__ import annotations

import logging

from app.content.level_resources import fighter_second_wind_uses
from app.content.pregen_attacks import build_brom_greataxe_attack, build_selene_longbow_attack
from app.content.pregen_equipment import (
    build_archer_fighter_visual_loadout,
    build_heavy_fighter_visual_loadout,
)
from app.content.rogue_attacks import build_mara_shortbow_attack, build_mara_shortsword_attack
from app.content.rogue_equipment import build_rogue_visual_loadout
from app.domain.models import CombatantTemplate, ResourceDefinition

logger = logging.getLogger(__name__)


def _second_wind(level: int) -> list[ResourceDefinition]:
    return [
        ResourceDefinition(
            id="second-wind",
            name="Second Wind",
            max_uses=fighter_second_wind_uses(level),
        )
    ]


def build_brom_ironmark() -> CombatantTemplate:
    try:
        level = 1
        return CombatantTemplate(
            id="brom-ironmark-l1",
            name="Brom Ironmark",
            archetype="Fighter",
            level=level,
            kind="character",
            armor_class=17,
            max_hp=12,
            speed_ft=30,
            initiative_bonus=1,
            weapon_attack=build_brom_greataxe_attack(),
            saving_throw_bonuses={
                "strength": 5, "dexterity": 1, "constitution": 4,
                "intelligence": 0, "wisdom": 1, "charisma": -1,
            },
            skill_bonuses={"athletics": 5, "acrobatics": 1},
            fighting_style="Defense",
            weapon_masteries=["greataxe", "greatsword", "halberd"],
            visual=build_heavy_fighter_visual_loadout(),
            resources=_second_wind(level),
            source="Original pregen built from SRD 5.2.1 Fighter level 1 rules",
        )
    except Exception as exc:
        logger.exception("Failed to build Brom Ironmark pregen.")
        raise RuntimeError("Brom Ironmark could not be created.") from exc


def build_selene_asharrow() -> CombatantTemplate:
    try:
        level = 1
        return CombatantTemplate(
            id="selene-asharrow-l1",
            name="Selene Asharrow",
            archetype="Fighter",
            level=level,
            kind="character",
            armor_class=16,
            max_hp=12,
            speed_ft=30,
            initiative_bonus=3,
            weapon_attack=build_selene_longbow_attack(),
            saving_throw_bonuses={
                "strength": 3, "dexterity": 3, "constitution": 4,
                "intelligence": 0, "wisdom": 1, "charisma": -1,
            },
            skill_bonuses={"athletics": 1, "acrobatics": 5},
            fighting_style="Archery",
            weapon_masteries=["greataxe", "greatsword", "halberd"],
            visual=build_archer_fighter_visual_loadout(),
            resources=_second_wind(level),
            source="Original pregen built from SRD 5.2.1 Fighter level 1 rules",
        )
    except Exception as exc:
        logger.exception("Failed to build Selene Asharrow pregen.")
        raise RuntimeError("Selene Asharrow could not be created.") from exc


def build_mara_quickstep() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="mara-quickstep-l1",
            name="Mara Quickstep",
            archetype="Rogue",
            level=1,
            kind="character",
            armor_class=14,
            max_hp=10,
            speed_ft=30,
            initiative_bonus=3,
            weapon_attack=build_mara_shortsword_attack(),
            alternate_weapon_attacks=[build_mara_shortbow_attack()],
            saving_throw_bonuses={
                "strength": 0, "dexterity": 5, "constitution": 2,
                "intelligence": 3, "wisdom": 1, "charisma": -1,
            },
            skill_bonuses={"athletics": 0, "acrobatics": 5},
            weapon_masteries=["dagger", "rapier"],
            visual=build_rogue_visual_loadout(),
            source="Original pregen built from SRD 5.2.1 Rogue level 1 rules",
        )
    except Exception as exc:
        logger.exception("Failed to build Mara Quickstep pregen.")
        raise RuntimeError("Mara Quickstep could not be created.") from exc
