from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)
_BLOOD_FRENZY = "Blood Frenzy"


def bound_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return source traits that are fully bound to existing universal primitives."""
    try:
        if _BLOOD_FRENZY not in monster.trait_names:
            return frozenset()
        if not any(attack.kind == "melee" for attack in monster.attacks):
            return frozenset()
        return frozenset({_BLOOD_FRENZY})
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
