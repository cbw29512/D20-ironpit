"""Source-semantic 2014 Damage Transfer binding."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.damage_transfer import DamageTransferRule

logger = logging.getLogger(__name__)

_RULE = re.compile(
    r"While (?:attached to a creature|it is grappling a creature), the .+? takes "
    r"only half the damage dealt to it(?: \(rounded down\))?, and (?:that creature|"
    r"the creature grappled by the .+?) takes the other half\.",
    re.IGNORECASE,
)


def damage_transfer_rule_2014(monster: SourceMonster2014) -> DamageTransferRule | None:
    """Compile the exact printed split only when the complete clause matches."""
    try:
        candidates = [
            (heading, " ".join(text.split()))
            for heading, text in source_sections_2014(
                monster.source_traits, include_continuations=True,
            ).items()
            if "takes only half the damage dealt to it" in text.casefold()
            or "takes the other half" in text.casefold()
        ]
        if not candidates:
            return None
        if len(candidates) != 1 or _RULE.fullmatch(candidates[0][1]) is None:
            raise ValueError("Damage Transfer printed source proof is incomplete.")
        return DamageTransferRule(source_name=candidates[0][0])
    except Exception:
        logger.exception("Failed 2014 Damage Transfer source proof for %s.", monster.name)
        raise
