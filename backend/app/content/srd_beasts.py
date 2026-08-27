from __future__ import annotations

import logging

from app.content.srd_beast_actions import build_lion_roar_action
from app.content.srd_beast_attacks import (
    build_giant_crab_claw_attack,
    build_lion_rend_attack,
    build_wolf_bite_attack,
)
from app.domain.models import Ability, CombatantTemplate, MultiattackDefinition, SizeCategory, VisualLoadout

logger = logging.getLogger(__name__)


def build_wolf() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-wolf",
            name="Wolf",
            archetype="Wolf",
            challenge_rating="1/4",
            kind="monster",
            size=SizeCategory.MEDIUM,
            armor_class=12,
            max_hp=11,
            speed_ft=40,
            initiative_bonus=2,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 2,
                Ability.DEXTERITY: 2,
                Ability.CONSTITUTION: 1,
                Ability.INTELLIGENCE: -4,
                Ability.WISDOM: 1,
                Ability.CHARISMA: -2,
            },
            weapon_attack=build_wolf_bite_attack(),
            visual=VisualLoadout(armor="none", main_hand="bite", body_style="beast"),
            source="SRD 5.2.1 Wolf",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Wolf.")
        raise RuntimeError("Wolf could not be created.") from exc


def build_giant_crab() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-giant-crab",
            name="Giant Crab",
            archetype="Giant Crab",
            challenge_rating="1/8",
            kind="monster",
            size=SizeCategory.MEDIUM,
            armor_class=15,
            max_hp=13,
            speed_ft=30,
            initiative_bonus=1,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 1,
                Ability.DEXTERITY: 1,
                Ability.CONSTITUTION: 0,
                Ability.INTELLIGENCE: -5,
                Ability.WISDOM: -1,
                Ability.CHARISMA: -4,
            },
            weapon_attack=build_giant_crab_claw_attack(),
            visual=VisualLoadout(armor="shell", main_hand="claw", body_style="beast"),
            source="SRD 5.2.1 Giant Crab",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Giant Crab.")
        raise RuntimeError("Giant Crab could not be created.") from exc


def build_lion() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-lion",
            name="Lion",
            archetype="Lion",
            challenge_rating="1",
            kind="monster",
            size=SizeCategory.LARGE,
            armor_class=12,
            max_hp=22,
            speed_ft=50,
            initiative_bonus=2,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 3,
                Ability.DEXTERITY: 2,
                Ability.CONSTITUTION: 0,
                Ability.INTELLIGENCE: -4,
                Ability.WISDOM: 1,
                Ability.CHARISMA: -1,
            },
            weapon_attack=build_lion_rend_attack(),
            save_actions=[build_lion_roar_action()],
            multiattack=MultiattackDefinition(
                id="lion-multiattack",
                name="Multiattack",
                attack_count=2,
                allowed_attack_ids=["lion-rend"],
                replacement_save_action_ids=["lion-roar"],
                max_save_replacements=1,
            ),
            visual=VisualLoadout(armor="none", main_hand="rend", body_style="beast"),
            source="SRD 5.2.1 Lion",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Lion.")
        raise RuntimeError("Lion could not be created.") from exc
