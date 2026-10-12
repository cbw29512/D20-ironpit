"""2014 opening-initiative source proof, separate from universal combat behavior."""
from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

_TRIGGER = "round1_initiative_lead"
_PRINTED_BONUS = re.compile(r"extra\s+7\s+\((2)d(6)\)\s+damage", re.IGNORECASE)


def opening_initiative_damage_source_2014(monster: SourceMonster2014) -> str | None:
    """Return the printed trait name only after its immutable dice and modes agree."""
    try:
        if monster.id != "bugbear" or "Surprise Attack" not in monster.trait_names:
            return None
        source = " ".join(html.unescape(
            re.sub(r"<[^>]+>", " ", monster.source_traits or "")
        ).split())
        text = source.casefold()
        if not all(fragment in text for fragment in (
            "surprise attack.", "surprises a creature",
            "hits it with an attack during the first round of combat",
        )) or _PRINTED_BONUS.search(source) is None:
            raise ValueError("Bugbear Surprise Attack printed source proof is incomplete.")
        if not monster.attacks:
            raise ValueError("Opening initiative attack source has no attacks.")
        for attack in monster.attacks:
            rows = attack.conditional_damage
            expected = {
                "trigger": _TRIGGER,
                "mode": "add",
                "dice_count": 2,
                "dice_size": 6,
                "damage_bonus": 0,
                "damage_type": "piercing",
            }
            if len(rows) != 1 or not isinstance(rows[0], dict) or rows[0] != expected:
                raise ValueError(f"{monster.name} {attack.name} initiative damage differs from source.")
        return "Surprise Attack"
    except Exception:
        logger.exception("Failed 2014 opening-initiative source proof for %s.", monster.name)
        raise
