from __future__ import annotations

import logging

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)

_BLOOD_FRENZY = "Blood Frenzy"
_RECKLESS = "Reckless"
_POOR_DEPTH_PERCEPTION = "Poor Depth Perception"
_RAMPAGE = "Rampage"


def supports_blood_frenzy_2014(monster: SourceMonster2014) -> bool:
    try:
        return _BLOOD_FRENZY in monster.trait_names and any(
            attack.kind == "melee" for attack in monster.attacks
        )
    except Exception:
        logger.exception("Failed to classify 2014 Blood Frenzy for %s.", monster.name)
        raise


def supports_reckless_2014(monster: SourceMonster2014) -> bool:
    """Return whether printed Reckless can use the shared melee-Strength resolver."""
    try:
        if _RECKLESS not in monster.trait_names:
            return False
        melee = [attack for attack in monster.attacks if attack.kind == "melee"]
        return bool(melee) and all(attack.attack_ability == "strength" for attack in melee)
    except Exception:
        logger.exception("Failed to classify 2014 Reckless support for %s.", monster.name)
        raise


def supports_poor_depth_perception_2014(monster: SourceMonster2014) -> bool:
    """Existing range rules already impose the printed beyond-30-foot Disadvantage."""
    try:
        if _POOR_DEPTH_PERCEPTION not in monster.trait_names:
            return False
        ranged = [attack for attack in monster.attacks if attack.kind == "ranged"]
        return bool(ranged) and all(
            attack.normal_range_ft is not None and attack.normal_range_ft <= 30
            for attack in ranged
        )
    except Exception:
        logger.exception("Failed Poor Depth Perception classification for %s.", monster.name)
        raise


def bonus_attack_grants_2014(monster: SourceMonster2014) -> list[BonusAttackGrant]:
    """Bind printed kill-triggered Bonus Action attacks to the shared grant primitive."""
    try:
        if _RAMPAGE not in monster.trait_names:
            return []
        bites = [
            attack for attack in monster.attacks
            if attack.kind == "melee" and attack.name == "Bite"
        ]
        if len(bites) != 1:
            raise ValueError(f"{monster.name} Rampage requires exactly one melee Bite attack.")
        return [BonusAttackGrant(
            id=f"{monster.id}-rampage",
            name=_RAMPAGE,
            attack_ids=[attack_id_2014(monster, bites[0].id)],
            attack_count=1,
            trigger="source_melee_zero_hp_this_turn",
            priority=10,
        )]
    except Exception:
        logger.exception("Failed to bind 2014 Rampage for %s.", monster.name)
        raise


def conditional_attack_advantage_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> list[ConditionalAttackAdvantage]:
    """Bind Blood Frenzy to the shared target-not-full-HP Advantage primitive."""
    try:
        if not supports_blood_frenzy_2014(monster) or attack.kind != "melee":
            return []
        return [ConditionalAttackAdvantage(trigger="target_not_full_hp")]
    except Exception:
        logger.exception(
            "Failed to bind conditional attack Advantage for %s / %s.",
            monster.name,
            attack.name,
        )
        raise


def bound_attack_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    try:
        bound: set[str] = set()
        if supports_blood_frenzy_2014(monster):
            bound.add(_BLOOD_FRENZY)
        if supports_reckless_2014(monster):
            bound.add(_RECKLESS)
        if supports_poor_depth_perception_2014(monster):
            bound.add(_POOR_DEPTH_PERCEPTION)
        if bonus_attack_grants_2014(monster):
            bound.add(_RAMPAGE)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to classify attack traits for %s.", monster.name)
        raise
