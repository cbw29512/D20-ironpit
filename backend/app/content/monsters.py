from __future__ import annotations

import logging

from app.content.monster_attacks import (
    build_axe_beak_attack,
    build_bandit_light_crossbow_attack,
    build_bandit_scimitar_attack,
    build_commoner_club_attack,
    build_giant_lizard_attack,
)
from app.content.monster_equipment import build_monster_visual
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def _monster(**kwargs) -> CombatantTemplate:
    try:
        return CombatantTemplate(kind="monster", **kwargs)
    except Exception as exc:
        monster_id = kwargs.get("id", "unknown")
        logger.exception("Failed to build monster %s.", monster_id)
        raise RuntimeError(f"Monster {monster_id} could not be created.") from exc


def build_bandit() -> CombatantTemplate:
    return _monster(
        id="srd-bandit",
        name="Bandit",
        archetype="Bandit",
        challenge_rating="1/8",
        armor_class=12,
        max_hp=11,
        speed_ft=30,
        initiative_bonus=1,
        weapon_attack=build_bandit_scimitar_attack(),
        alternate_weapon_attacks=[build_bandit_light_crossbow_attack()],
        visual=build_monster_visual("leather", "scimitar", "humanoid"),
        source="SRD 5.2.1 Bandit",
    )


def build_commoner() -> CombatantTemplate:
    return _monster(
        id="srd-commoner",
        name="Commoner",
        archetype="Commoner",
        challenge_rating="0",
        armor_class=10,
        max_hp=4,
        speed_ft=30,
        initiative_bonus=0,
        weapon_attack=build_commoner_club_attack(),
        visual=build_monster_visual("clothes", "club", "humanoid"),
        source="SRD 5.2.1 Commoner",
    )


def build_axe_beak() -> CombatantTemplate:
    return _monster(
        id="srd-axe-beak",
        name="Axe Beak",
        archetype="Axe Beak",
        challenge_rating="1/4",
        size="large",
        armor_class=11,
        max_hp=19,
        speed_ft=50,
        initiative_bonus=1,
        weapon_attack=build_axe_beak_attack(),
        visual=build_monster_visual("none", "beak", "axe-beak"),
        source="SRD 5.2.1 p. 260 Axe Beak",
    )


def build_giant_lizard() -> CombatantTemplate:
    return _monster(
        id="srd-giant-lizard",
        name="Giant Lizard",
        archetype="Giant Lizard",
        challenge_rating="1/4",
        size="large",
        armor_class=12,
        max_hp=19,
        speed_ft=40,
        initiative_bonus=1,
        weapon_attack=build_giant_lizard_attack(),
        visual=build_monster_visual("natural", "bite", "giant-lizard"),
        source="SRD 5.2.1 Giant Lizard",
    )
