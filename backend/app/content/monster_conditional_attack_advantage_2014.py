from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)

ATTACK_MODELED_TRAITS_2014 = frozenset({"Blood Frenzy"})


def conditional_attack_advantage_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> list[ConditionalAttackAdvantage]:
    """Compile source-declared 2014 traits into reusable attack Advantage specs."""
    try:
        if "Blood Frenzy" not in monster.trait_names or attack.kind != "melee":
            return []
        return [ConditionalAttackAdvantage(trigger="target_not_full_hp")]
    except Exception:
        logger.exception(
            "Failed to compile 2014 conditional attack Advantage for %s / %s.",
            monster.name,
            attack.name,
        )
        raise
