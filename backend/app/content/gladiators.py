from __future__ import annotations

import logging

from app.content.equipment import build_longsword
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack

logger = logging.getLogger(__name__)


def build_mara_stone() -> CombatantTemplate:
    """Original Level 5 Fighter pregen built on SRD 5.2.1 Fighter progression."""
    try:
        return CombatantTemplate(
            id="mara-stone-l5",
            name="Mara Stone",
            archetype="Fighter",
            level=5,
            kind="character",
            armor_class=19,
            max_hp=44,
            speed_ft=30,
            initiative_bonus=2,
            attacks_per_action=2,
            weapon_attack=WeaponAttack(
                id="mara-longsword",
                weapon=build_longsword(),
                attack_bonus=7,
                damage_bonus=4,
            ),
            fighting_style="Defense",
            weapon_masteries=["longsword"],
            visual=VisualLoadout(
                armor="chain-mail",
                main_hand="longsword",
                off_hand="shield",
                body_style="humanoid",
            ),
            resources=[ResourceDefinition(id="second-wind", name="Second Wind", max_uses=3)],
            source="Original Level 5 Fighter pregen using SRD 5.2.1 progression",
        )
    except Exception as exc:
        logger.exception("Failed to build Mara Stone.")
        raise RuntimeError("Mara Stone could not be created.") from exc
