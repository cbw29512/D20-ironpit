from __future__ import annotations

import logging

from app.content.srd_attacks import build_knight_crossbow_attack, build_knight_greatsword_attack
from app.content.srd_boss_attacks import (
    build_tough_boss_crossbow_attack,
    build_tough_boss_warhammer_attack,
)
from app.domain.models import (
    Ability,
    CombatantTemplate,
    ConditionType,
    CreatureType,
    MultiattackDefinition,
    SizeCategory,
    VisualLoadout,
)

logger = logging.getLogger(__name__)


def build_knight() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-knight",
            name="Knight",
            archetype="Knight",
            challenge_rating="3",
            kind="monster",
            creature_type=CreatureType.HUMANOID,
            size=SizeCategory.MEDIUM,
            armor_class=18,
            max_hp=52,
            speed_ft=30,
            initiative_bonus=0,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 3,
                Ability.DEXTERITY: 0,
                Ability.CONSTITUTION: 2,
                Ability.INTELLIGENCE: 0,
                Ability.WISDOM: 0,
                Ability.CHARISMA: 2,
            },
            saving_throw_modifiers={
                Ability.CONSTITUTION: 4,
                Ability.WISDOM: 2,
            },
            condition_immunities=[ConditionType.FRIGHTENED],
            weapon_attack=build_knight_greatsword_attack(),
            alternate_weapon_attacks=[build_knight_crossbow_attack()],
            multiattack=MultiattackDefinition(
                id="knight-multiattack",
                name="Multiattack",
                attack_count=2,
                allowed_attack_ids=["knight-greatsword", "knight-heavy-crossbow"],
            ),
            visual=VisualLoadout(
                armor="plate-armor",
                main_hand="greatsword",
                body_style="humanoid",
            ),
            source="SRD 5.2.1 Knight",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Knight.")
        raise RuntimeError("Knight could not be created.") from exc


def build_tough_boss() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-tough-boss",
            name="Tough Boss",
            archetype="Tough Boss",
            challenge_rating="4",
            kind="monster",
            creature_type=CreatureType.HUMANOID,
            size=SizeCategory.MEDIUM,
            armor_class=16,
            max_hp=82,
            speed_ft=30,
            initiative_bonus=2,
            weapon_attack=build_tough_boss_warhammer_attack(),
            alternate_weapon_attacks=[build_tough_boss_crossbow_attack()],
            multiattack=MultiattackDefinition(
                id="tough-boss-multiattack",
                name="Multiattack",
                attack_count=2,
                allowed_attack_ids=[
                    "tough-boss-warhammer",
                    "tough-boss-heavy-crossbow",
                ],
            ),
            visual=VisualLoadout(
                armor="chain-mail",
                main_hand="warhammer",
                body_style="humanoid",
            ),
            source="SRD 5.2.1 Tough Boss",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Tough Boss.")
        raise RuntimeError("Tough Boss could not be created.") from exc
