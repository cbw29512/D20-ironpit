from __future__ import annotations

import logging

from app.content.srd_beast_attacks import build_wolf_bite_attack
from app.domain.models import Ability, CombatantTemplate, SizeCategory, VisualLoadout

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
            visual=VisualLoadout(
                armor="none",
                main_hand="bite",
                body_style="beast",
            ),
            source="SRD 5.2.1 Wolf",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Wolf.")
        raise RuntimeError("Wolf could not be created.") from exc
