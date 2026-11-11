"""Bind printed Grappler to the existing own-Grapple attack Advantage rule.

Printed source and immutable card provide identity; runtime never dispatches
on monster or ability name. No Grapple is created by this passive.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)

_PRINTED_GRAPPLER = (
    r"The (?P<owner>[a-z][a-z -]*) has advantage on attack rolls "
    r"against any creature grappled by it\."
)


def source_grapple_attack_advantage_2014(
    monster: SourceMonster2014,
) -> list[ConditionalAttackAdvantage]:
    """Prove complete source text before binding the existing universal trigger."""
    try:
        if "Grappler" not in monster.trait_names:
            return []
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Grappler", "")
        # The generic predicate is 'grappled by acting source', not every
        # Grappled target; no bonus is granted when another creature holds it.
        if re.fullmatch(_PRINTED_GRAPPLER, printed, flags=re.IGNORECASE) is None:
            return []
        return [ConditionalAttackAdvantage(trigger="target_grappled_by_self")]
    except Exception:
        logger.exception("Could not certify source-owned attack Advantage for %s", monster.id)
        raise
