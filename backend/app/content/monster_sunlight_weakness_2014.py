"""Source-verified 2014 sunlight reaction; behavior belongs to universal roll modifiers."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.environment_contexts import EnvironmentContextReaction

logger = logging.getLogger(__name__)

_PRINTED_NAME = "Sunlight Weakness"
_REQUIRED_CLAUSES = (
    "while in sunlight",
    "disadvantage on attack rolls",
    "ability checks",
    "saving throws",
)


def source_sunlight_weakness_2014(
    monster: SourceMonster2014,
) -> EnvironmentContextReaction | None:
    """Bind a permanent passive only when its complete printed clause is proven.

    The standard Pit has no sunlight, but an active source-owned sunlight
    emitter can supply that context during a fight. This passive is never
    represented as an arena-neutral exemption or mutable card state.
    """
    try:
        if _PRINTED_NAME not in monster.trait_names:
            return None
        clause = source_sections_2014(monster.source_traits).get(_PRINTED_NAME, "")
        folded = clause.casefold()
        if not all(phrase in folded for phrase in _REQUIRED_CLAUSES):
            return None
        return EnvironmentContextReaction(
            source_id="sunlight-weakness",
            source_name=_PRINTED_NAME,
            context_id="sunlight",
            disadvantage_on=["attack_rolls", "ability_checks", "saving_throws"],
        )
    except Exception:
        logger.exception("Failed 2014 sunlight reaction source proof for %s.", monster.id)
        raise
