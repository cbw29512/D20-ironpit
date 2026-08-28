from __future__ import annotations

import logging

from app.content.pregen_attacks import build_brom_greataxe_attack
from app.content.pregen_equipment import build_heavy_fighter_visual_loadout
from app.domain.models import CombatantTemplate, ResourceDefinition

logger = logging.getLogger(__name__)


def build_brom_ironmark() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="brom-ironmark-l1",
            name="Brom Ironmark",
            archetype="Fighter",
            level=1,
            kind="character",
            armor_class=17,
            max_hp=12,
            speed_ft=30,
            initiative_bonus=1,
            weapon_attack=build_brom_greataxe_attack(),
            fighting_style="Defense",
            weapon_masteries=["greataxe", "greatsword", "halberd"],
            visual=build_heavy_fighter_visual_loadout(),
            resources=[
                ResourceDefinition(id="second-wind", name="Second Wind", max_uses=2),
            ],
            source="Original pregen built from SRD 5.2.1 Fighter level 1 rules",
        )
    except Exception as exc:
        logger.exception("Failed to build Brom Ironmark pregen.")
        raise RuntimeError("Brom Ironmark could not be created.") from exc
