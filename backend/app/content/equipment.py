from __future__ import annotations

import logging

from app.content.weapon_catalog import build_weapon
from app.domain.models import VisualLoadout, Weapon

logger = logging.getLogger(__name__)


def _audited(weapon_id: str) -> Weapon:
    try:
        return build_weapon(weapon_id)
    except Exception as exc:
        logger.exception("Failed to build audited weapon %s.", weapon_id)
        raise RuntimeError(f"Weapon {weapon_id} could not be created.") from exc


def build_greatsword() -> Weapon:
    return _audited("greatsword")


def build_longsword() -> Weapon:
    return _audited("longsword")


def build_scimitar() -> Weapon:
    return _audited("scimitar")


def build_shortsword() -> Weapon:
    return _audited("shortsword")


def build_longbow() -> Weapon:
    return _audited("longbow")


def build_shortbow() -> Weapon:
    return _audited("shortbow")


def build_fighter_visual_loadout() -> VisualLoadout:
    try:
        return VisualLoadout(
            armor="chain-mail",
            main_hand="longsword",
            off_hand="shield",
            body_style="humanoid",
        )
    except Exception as exc:
        logger.exception("Failed to build Fighter visual loadout.")
        raise RuntimeError("Fighter visual loadout could not be created.") from exc


def build_goblin_visual_loadout() -> VisualLoadout:
    try:
        return VisualLoadout(
            armor="leather",
            main_hand="scimitar",
            off_hand="shield",
            body_style="goblinoid",
        )
    except Exception as exc:
        logger.exception("Failed to build Goblin visual loadout.")
        raise RuntimeError("Goblin visual loadout could not be created.") from exc
