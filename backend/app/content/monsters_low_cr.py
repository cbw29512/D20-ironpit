from __future__ import annotations

import logging

from app.content.monster_attacks import (
    build_giant_rat_attack,
    build_giant_weasel_attack,
    build_guard_spear_melee_attack,
    build_guard_spear_thrown_attack,
)
from app.content.monster_equipment import build_monster_visual
from app.domain.models import CombatTrait, CombatantTemplate

logger = logging.getLogger(__name__)


def _monster(**kwargs) -> CombatantTemplate:
    try:
        return CombatantTemplate(kind="monster", **kwargs)
    except Exception as exc:
        monster_id = kwargs.get("id", "unknown")
        logger.exception("Failed to build monster %s.", monster_id)
        raise RuntimeError(f"Monster {monster_id} could not be created.") from exc


def build_guard() -> CombatantTemplate:
    return _monster(
        id="srd-guard", name="Guard", archetype="Guard", challenge_rating="1/8",
        armor_class=16, max_hp=11, speed_ft=30, initiative_bonus=1,
        weapon_attack=build_guard_spear_melee_attack(),
        alternate_weapon_attacks=[build_guard_spear_thrown_attack()],
        visual=build_monster_visual("chain-shirt", "spear", "humanoid"),
        source="SRD 5.2.1 Guard",
    )


def build_giant_rat() -> CombatantTemplate:
    return _monster(
        id="srd-giant-rat", name="Giant Rat", archetype="Giant Rat", challenge_rating="1/8",
        size="small", armor_class=13, max_hp=7, speed_ft=30, initiative_bonus=3,
        weapon_attack=build_giant_rat_attack(),
        combat_traits=[CombatTrait.PACK_TACTICS],
        visual=build_monster_visual("none", "bite", "giant-rat"),
        source="SRD 5.2.1 Giant Rat",
    )


def build_giant_weasel() -> CombatantTemplate:
    return _monster(
        id="srd-giant-weasel", name="Giant Weasel", archetype="Giant Weasel", challenge_rating="1/8",
        armor_class=13, max_hp=9, speed_ft=40, initiative_bonus=3,
        weapon_attack=build_giant_weasel_attack(),
        visual=build_monster_visual("none", "bite", "giant-weasel"),
        source="SRD 5.2.1 Giant Weasel",
    )
