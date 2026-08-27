from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate, DamageType, VisualLoadout, Weapon

logger = logging.getLogger(__name__)


def build_demo_fighter() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="aldric-vane-l1",
            name="Aldric Vane",
            level=1,
            kind="character",
            armor_class=18,
            max_hp=12,
            initiative_bonus=1,
            weapon=Weapon(
                name="Longsword",
                attack_bonus=5,
                dice_count=1,
                dice_size=8,
                damage_bonus=3,
                damage_type=DamageType.SLASHING,
                animation="slash",
            ),
            visual=VisualLoadout(
                armor="chain-mail",
                main_hand="longsword",
                off_hand="shield",
            ),
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
            kind="monster",
            armor_class=15,
            max_hp=10,
            initiative_bonus=2,
            weapon=Weapon(
                name="Scimitar",
                attack_bonus=4,
                dice_count=1,
                dice_size=6,
                damage_bonus=2,
                damage_type=DamageType.SLASHING,
                animation="slash",
            ),
            visual=VisualLoadout(
                armor="leather",
                main_hand="scimitar",
                off_hand="shield",
                body_style="goblinoid",
            ),
            source="SRD 5.2.1 Goblin Warrior",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD goblin warrior.")
        raise RuntimeError("Goblin Warrior could not be created.") from exc
