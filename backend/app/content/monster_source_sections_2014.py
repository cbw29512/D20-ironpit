from __future__ import annotations
from html import unescape
import logging
import re
logger = logging.getLogger(__name__)

def source_sections_2014(source: str | None) -> dict[str, str]:
    try:
        sections = {}
        for paragraph in re.findall(r"<p>(.*?)</p>", source or "", re.S):
            heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.S)
            if heading:
                name = unescape(re.sub(r"<[^>]*>", "", heading[1])).rstrip(".")
                body = re.sub(r"<[^>]*>", "", paragraph[heading.end():])
                sections[name] = " ".join(unescape(body).split())
        return sections
    except Exception:
        logger.exception("Failed to read 2014 source sections.")
        raise


def requires_two_hands_2014(monster, attack) -> bool:
    """Recognize the preserved conditional damage profile from printed action text."""
    try:
        if attack.kind != "melee":
            return False
        text = source_sections_2014(monster.source_actions).get(attack.name, "")
        match = re.search(r"or \d+ \((\d+)d(\d+) \+ (\d+)\) \w+ damage if used with two hands", text)
        return bool(match and tuple(map(int, match.groups())) == (
            attack.damage.dice_count, attack.damage.dice_size, attack.damage.bonus
        ))
    except Exception:
        logger.exception("Failed conditional two-hand source proof for %s / %s.", monster.id, attack.id)
        raise
