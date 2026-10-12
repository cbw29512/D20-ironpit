"""2014 source-derived, source-proven special-sense profiles."""
from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)
_BOUNDED = re.compile(
    r"\bblindsight\s+(\d+)\s*ft\.\s+or\s+(\d+)\s*ft\.\s+"
    r"while\s+deafened\s*\(\s*blind\s+beyond\s+this\s+radius\s*\)",
    re.IGNORECASE,
)
_BLIND_TRAIT = re.compile(
    r"\bBlind Senses\s*\.\s*The\s+[^.]+?\s+can['’]t\s+use\s+its\s+blindsight"
    r"\s+while\s+deafened\s+and\s+unable\s+to\s+smell\.",
    re.IGNORECASE,
)


def bounded_blindsight_2014(monster: SourceMonster2014) -> tuple[int, int] | None:
    """Return full/reduced source ranges only when sensing qualifiers are proven."""
    try:
        if "Blind Senses" not in monster.trait_names:
            return None
        source = monster.senses or ""
        match = _BOUNDED.search(source)
        traits = " ".join(html.unescape(re.sub(r"<[^>]*>", " ", monster.source_traits or "")).split())
        if not match or not _BLIND_TRAIT.search(traits):
            return None
        if len(_BOUNDED.findall(source)) != 1 or re.search(r"\btruesight\b", source, re.I):
            return None
        normal, deafened = map(int, match.groups())
        if not 0 < deafened < normal <= 1000:
            return None
        return normal, deafened
    except Exception:
        logger.exception("2014 bounded Blindsight source proof failed for %s.", monster.id)
        raise


def special_senses_2014(monster: SourceMonster2014) -> tuple[int, int]:
    """Bind only complete, unconditional source-declared special sight ranges."""
    try:
        source = monster.senses
        if not isinstance(source, str):
            raise ValueError("2014 monster special senses must be source text.")
        bounded = bounded_blindsight_2014(monster)
        if bounded is not None:
            return bounded[0], 0
        ranges: list[int] = []
        for name in ("blindsight", "truesight"):
            found = re.findall(rf"\b{name}\b", source, re.I)
            matches = re.findall(rf"\b{name}\s+(\d+)\s*ft\.", source, re.I)
            if len(found) != len(matches) or len(matches) > 1:
                raise ValueError(f"Unsupported {name} source syntax for {monster.id}.")
            amount = int(matches[0]) if matches else 0
            if amount > 1000:
                raise ValueError(f"Out-of-bounds {name} range for {monster.id}.")
            if name == "blindsight" and re.search(
                r"\bblind\s+beyond\s+this\s+radius\b", source, re.I,
            ):
                amount = 0
            ranges.append(amount)
        return ranges[0], ranges[1]
    except Exception:
        logger.exception("2014 special-sense binding failed for %s.", monster.id)
        raise
