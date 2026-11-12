"""Source-semantic 2014 passive Freedom of Movement binding."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.shared_movement_spells_2014 import freedom_of_movement_debuff_counters_2014
from app.domain.progression import PassiveDebuffCounterGrant

logger = logging.getLogger(__name__)

_PINNED = (
    "the kraken ignores difficult terrain, and magical effects can't reduce its speed "
    "or cause it to be restrained. it can spend 5 feet of movement to escape from "
    "nonmagical restraints or being grappled."
)


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace("’", "'").split())


def passive_freedom_of_movement_grants_2014(
    monster: SourceMonster2014,
) -> list[PassiveDebuffCounterGrant]:
    """Bind only the complete printed passive clause, independent of card identity."""
    try:
        matches = [
            heading
            for heading, body in source_sections_2014(
                monster.source_traits, include_continuations=True,
            ).items()
            if _normalized(body) == _PINNED
        ]
        if not matches:
            return []
        if len(matches) != 1:
            raise ValueError(f"{monster.name} has ambiguous passive movement clauses.")
        source_name = matches[0]
        return [
            PassiveDebuffCounterGrant(
                source_id=f"passive-freedom-of-movement-{index}",
                source_name=source_name,
                counter=counter,
            )
            for index, counter in enumerate(
                freedom_of_movement_debuff_counters_2014(
                    prevents_magical_paralysis=False,
                )
            )
        ]
    except Exception:
        logger.exception("Failed passive Freedom of Movement proof for %s.", monster.id)
        raise


def bound_passive_freedom_of_movement_traits_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Return the printed label only when every passive clause is represented."""
    return frozenset(
        grant.source_name for grant in passive_freedom_of_movement_grants_2014(monster)
    )
