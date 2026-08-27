from __future__ import annotations

import logging

from app.domain.models import ConditionalDamage, DamageType, VisualLoadout, Weapon

logger = logging.getLogger(__name__)


def build_longsword() -> Weapon:
    """Return the MVP Fighter's reusable longsword record."""
    try:
        return Weapon(
            name="Longsword",
            attack_bonus=5,
            dice_count=1,
            dice_size=8,
            damage_bonus=3,
            damage_type=DamageType.SLASHING,
            animation="slash",
        )
    except Exception as exc:
        logger.exception("Failed to build longsword content record.")
        raise RuntimeError("Longsword content could not be created.") from exc


def build_scimitar() -> Weapon:
    """Return the SRD Goblin Warrior's reusable scimitar record."""
    try:
        return Weapon(
            name="Scimitar",
            attack_bonus=4,
            dice_count=1,
            dice_size=6,
            damage_bonus=2,
            damage_type=DamageType.SLASHING,
            animation="slash",
            conditional_damage=[
                ConditionalDamage(
                    trigger="attack_advantage",
                    dice_count=1,
                    dice_size=4,
                    damage_type=DamageType.SLASHING,
                )
            ],
        )
    except Exception as exc:
        logger.exception("Failed to build scimitar content record.")
        raise RuntimeError("Scimitar content could not be created.") from exc


def build_fighter_visual_loadout() -> VisualLoadout:
    """Return the Fighter's chain-mail, longsword, and shield presentation data."""
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
    """Return the Goblin's leather, scimitar, and shield presentation data."""
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
