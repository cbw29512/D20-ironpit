from __future__ import annotations

import logging

from app.content.equipment import (
    FIGHTER_CHAIN_MAIL_LOADOUT,
    GOBLIN_LEATHER_LOADOUT,
    LONGSWORD,
    SCIMITAR,
)
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
            armor_class=18,
            max_hp=12,
            initiative_bonus=1,
            weapon=LONGSWORD.model_copy(deep=True),
            visual=FIGHTER_CHAIN_MAIL_LOADOUT.model_copy(deep=True),
            resources=[
                ResourceDefinition(id="second-wind", name="Second Wind", max_uses=2),
            ],
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
            armor_class=15,
            max_hp=10,
            initiative_bonus=2,
            weapon=SCIMITAR.model_copy(deep=True),
            visual=GOBLIN_LEATHER_LOADOUT.model_copy(deep=True),
            source="SRD 5.2.1 Goblin Warrior",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD goblin warrior.")
        raise RuntimeError("Goblin Warrior could not be created.") from exc
