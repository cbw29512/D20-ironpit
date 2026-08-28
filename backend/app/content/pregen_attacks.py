from __future__ import annotations

import logging

from app.content.pregen_equipment import build_greataxe
from app.domain.models import WeaponAttack

logger = logging.getLogger(__name__)


def build_brom_greataxe_attack() -> WeaponAttack:
    try:
        return WeaponAttack(
            id="brom-greataxe",
            weapon=build_greataxe(),
            attack_bonus=5,
            damage_bonus=3,
        )
    except Exception as exc:
        logger.exception("Failed to build Brom greataxe attack profile.")
        raise RuntimeError("Brom greataxe attack could not be created.") from exc
