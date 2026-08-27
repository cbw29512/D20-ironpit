from __future__ import annotations

import logging

from app.content.equipment import build_longsword
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack

logger = logging.getLogger(__name__)


def _fighter_resources(level: int, second_wind_uses: int) -> list[ResourceDefinition]:
    resources = [ResourceDefinition(id="second-wind", name="Second Wind", max_uses=second_wind_uses)]
    if level >= 2:
        resources.append(
            ResourceDefinition(
                id="action-surge",
                name="Action Surge",
                max_uses=2 if level >= 17 else 1,
            )
        )
    return resources


def _build_longsword_fighter(
    fighter_id: str,
    name: str,
    level: int,
    max_hp: int,
    attack_bonus: int,
    damage_bonus: int,
    attacks_per_action: int,
    second_wind_uses: int,
) -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id=fighter_id,
            name=name,
            archetype="Fighter",
            level=level,
            kind="character",
            armor_class=19,
            max_hp=max_hp,
            speed_ft=30,
            initiative_bonus=2,
            attacks_per_action=attacks_per_action,
            weapon_attack=WeaponAttack(
                id=f"{fighter_id}-longsword",
                weapon=build_longsword(),
                attack_bonus=attack_bonus,
                damage_bonus=damage_bonus,
            ),
            fighting_style="Defense",
            weapon_masteries=["longsword"],
            visual=VisualLoadout(
                armor="chain-mail",
                main_hand="longsword",
                off_hand="shield",
                body_style="humanoid",
            ),
            resources=_fighter_resources(level, second_wind_uses),
            source=f"Original Level {level} Fighter pregen using SRD 5.2.1 progression",
        )
    except Exception as exc:
        logger.exception("Failed to build Fighter pregen %s.", fighter_id)
        raise RuntimeError(f"Fighter pregen {fighter_id} could not be created.") from exc


def build_mara_stone() -> CombatantTemplate:
    return _build_longsword_fighter("mara-stone-l5", "Mara Stone", 5, 44, 7, 4, 2, 3)


def build_darius_flint() -> CombatantTemplate:
    return _build_longsword_fighter("darius-flint-l11", "Darius Flint", 11, 92, 9, 5, 3, 4)


def build_vera_ash() -> CombatantTemplate:
    return _build_longsword_fighter("vera-ash-l20", "Vera Ash", 20, 164, 11, 5, 4, 4)
