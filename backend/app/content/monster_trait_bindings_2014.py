from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)
_BLOOD_FRENZY = "Blood Frenzy"
_RECKLESS = "Reckless"


def supports_reckless_2014(monster: SourceMonster2014) -> bool:
    """Return whether printed Reckless can use the shared 2014 melee-Strength resolver."""
    try:
        if _RECKLESS not in monster.trait_names:
            return False
        melee = [attack for attack in monster.attacks if attack.kind == "melee"]
        return bool(melee) and all(attack.attack_ability == "strength" for attack in melee)
    except Exception:
        logger.exception("Failed to classify 2014 Reckless support for %s.", monster.name)
        raise


def bound_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return source traits that are fully bound to existing universal primitives."""
    try:
        bound: set[str] = set()
        if _BLOOD_FRENZY in monster.trait_names and any(attack.kind == "melee" for attack in monster.attacks):
            bound.add(_BLOOD_FRENZY)
        if supports_reckless_2014(monster):
            bound.add(_RECKLESS)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to classify bound 2014 traits for %s.", monster.name)
        raise


def conditional_attack_advantage_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> list[ConditionalAttackAdvantage]:
    """Bind Blood Frenzy to the shared target-not-full-HP Advantage primitive."""
    try:
        if _BLOOD_FRENZY not in bound_trait_names_2014(monster) or attack.kind != "melee":
            return []
        return [ConditionalAttackAdvantage(trigger="target_not_full_hp")]
    except Exception:
        logger.exception(
            "Failed to bind conditional attack Advantage for %s / %s.",
            monster.name,
            attack.name,
        )
        raise
