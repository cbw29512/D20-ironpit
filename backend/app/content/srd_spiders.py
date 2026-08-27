from __future__ import annotations

import logging

from app.content.srd_beast_actions import build_giant_spider_web_action
from app.content.srd_beast_attacks import build_giant_spider_bite_attack
from app.domain.models import Ability, CombatantTemplate, CreatureType, SizeCategory, VisualLoadout

logger = logging.getLogger(__name__)


def build_giant_spider() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-giant-spider",
            name="Giant Spider",
            archetype="Giant Spider",
            challenge_rating="1",
            kind="monster",
            creature_type=CreatureType.BEAST,
            size=SizeCategory.LARGE,
            armor_class=14,
            max_hp=26,
            speed_ft=30,
            initiative_bonus=3,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 2,
                Ability.DEXTERITY: 3,
                Ability.CONSTITUTION: 1,
                Ability.INTELLIGENCE: -4,
                Ability.WISDOM: 0,
                Ability.CHARISMA: -3,
            },
            weapon_attack=build_giant_spider_bite_attack(),
            save_actions=[build_giant_spider_web_action()],
            visual=VisualLoadout(
                armor="none",
                main_hand="bite",
                body_style="spider",
            ),
            source="SRD 5.2.1 Giant Spider",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Giant Spider.")
        raise RuntimeError("Giant Spider could not be created.") from exc
