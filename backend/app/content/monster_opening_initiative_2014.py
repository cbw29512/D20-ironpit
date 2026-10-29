"""Source-semantic 2014 surprise-opening proof, separate from runtime behavior."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_TRIGGER = "round1_initiative_lead"
_SURPRISE = re.compile(
    r"If the .+? surprises a creature and hits it with an attack during the first "
    r"round of combat, the target takes an extra (?P<average>\d+) "
    r"\((?P<count>\d+)d(?P<size>\d+)\) damage from the attack\.",
    re.IGNORECASE,
)
_AMBUSHER = re.compile(
    r"The .+? has advantage on attack rolls against any creature it has surprised\.",
    re.IGNORECASE,
)


def _sections(monster: SourceMonster2014) -> dict[str, str]:
    return source_sections_2014(monster.source_traits, include_continuations=True)


def opening_initiative_damage_source_2014(monster: SourceMonster2014) -> str | None:
    """Return the printed surprise-damage trait after card parameters agree."""
    try:
        candidates = [
            (heading, text, _SURPRISE.fullmatch(" ".join(text.split())))
            for heading, text in _sections(monster).items()
            if "surprises a creature" in text.casefold()
            and "first round of combat" in text.casefold()
        ]
        if not candidates:
            return None
        if len(candidates) != 1 or candidates[0][2] is None:
            raise ValueError("Surprise-opening printed source proof is incomplete.")
        heading, _, match = candidates[0]
        expected_average = int(match["count"]) * (int(match["size"]) + 1) // 2
        if int(match["average"]) != expected_average:
            raise ValueError("Surprise-opening printed source proof is incomplete.")
        if not monster.attacks:
            raise ValueError("Opening initiative attack source has no attacks.")
        for attack in monster.attacks:
            expected = {
                "trigger": _TRIGGER,
                "mode": "add",
                "dice_count": int(match["count"]),
                "dice_size": int(match["size"]),
                "damage_bonus": 0,
                "damage_type": str(attack.damage.type).casefold(),
            }
            rows = attack.conditional_damage
            if len(rows) != 1 or not isinstance(rows[0], dict) or rows[0] != expected:
                raise ValueError(f"{monster.name} {attack.name} initiative damage differs from source.")
        return heading
    except Exception:
        logger.exception("Failed 2014 opening-initiative damage proof for %s.", monster.name)
        raise


def opening_initiative_advantage_source_2014(monster: SourceMonster2014) -> str | None:
    """Return the printed surprise-Advantage trait after attack bindings agree."""
    try:
        candidates = [
            (heading, text, _AMBUSHER.fullmatch(" ".join(text.split())))
            for heading, text in _sections(monster).items()
            if "advantage on attack rolls" in text.casefold()
            and "creature it has surprised" in text.casefold()
        ]
        if not candidates:
            return None
        if len(candidates) != 1 or candidates[0][2] is None:
            raise ValueError("Surprise-Advantage printed source proof is incomplete.")
        if not monster.attacks:
            raise ValueError("Opening initiative Advantage source has no attacks.")
        expected = [{"trigger": _TRIGGER}]
        for attack in monster.attacks:
            if attack.conditional_attack_advantage != expected:
                raise ValueError(f"{monster.name} {attack.name} initiative Advantage differs from source.")
        return candidates[0][0]
    except Exception:
        logger.exception("Failed 2014 opening-initiative Advantage proof for %s.", monster.name)
        raise
