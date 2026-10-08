from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)
_BERSERK = re.compile(
    r"Berserk\s*\.\s*Whenever the [^.]+ starts its turn with (?P<hp>\d+) hit points or fewer, "
    r"roll a d6\s*\.\s*On a 6, the [^.]+ goes berserk\s*\.",
    re.IGNORECASE,
)


def berserk_self_buffs_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind printed 2014 golem Berserk to the shared self-buff path."""
    try:
        if "Berserk" not in monster.trait_names:
            return []
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", monster.source_traits or ""))).strip()
        match = _BERSERK.search(text)
        required = (
            "attacks the nearest creature it can see",
            "regains all its hit points",
        )
        if match is None or not all(fragment in text.casefold() for fragment in required):
            raise ValueError(f"{monster.name} Berserk source text does not match the supported 2014 arena semantics.")
        threshold = int(match.group("hp"))
        return [TimedSelfBuffAction(
            id="berserk",
            name="Berserk",
            activation_timing="start_turn",
            start_turn_max_current_hp=threshold,
            start_turn_roll_die_size=6,
            start_turn_roll_minimum=6,
            ends_at_full_hp=True,
            target_policy="nearest_visible_creature",
            expiry_timing=None,
            animation="rage",
        )]
    except Exception:
        logger.exception("Failed to bind 2014 Berserk for %s.", monster.name)
        raise
