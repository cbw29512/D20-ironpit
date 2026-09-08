from __future__ import annotations

import re

from app.domain.control_effects import ForcedMovementEffect
from app.domain.size import CreatureSize

_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_FORCED = re.compile(
    rf"(?:If the target is a (?P<size>{_SIZE}) or smaller creature, )?"
    r"(?:(?:the [A-Za-z’' -]+ )?(?P<active>pushes|pulls) the target|"
    r"the target is (?P<passive>pushed|pulled))\s+"
    r"(?P<upto>up to )?(?P<distance>\d+) feet"
    r"(?: straight)?\s+(?P<relation>away from|toward)\s+"
    r"(?P<anchor>itself|the [A-Za-z’' -]+?)"
    r"(?:\.(?=\s|$)|(?=,?\s+and\s+(?:(?:the target|it)\s+)?has\b))",
    re.I,
)


def _size(value: str | None) -> CreatureSize | None:
    return CreatureSize(value.lower()) if value else None


def parse_forced_movement_rider(text: str) -> tuple[str, ForcedMovementEffect | None, CreatureSize | None]:
    """Strip one exact push/pull clause while preserving printed distance semantics."""
    try:
        match = _FORCED.search(text)
        if match is None:
            return text, None, None
        verb = (match.group("active") or match.group("passive") or "").lower()
        relation = match.group("relation").lower()
        direction = "push" if verb.startswith("push") else "pull"
        if (direction == "push" and relation != "away from") or (direction == "pull" and relation != "toward"):
            raise ValueError("forced-movement verb and relative direction disagree")
        effect = ForcedMovementEffect(
            direction=direction,
            max_distance_ft=int(match.group("distance")),
            distance_mode="up_to" if match.group("upto") else "fixed",
        )
        clean = text[:match.start()] + " " + text[match.end():]
        return re.sub(r"\s+", " ", clean).strip(" ,"), effect, _size(match.group("size"))
    except (TypeError, ValueError) as exc:
        raise ValueError("forced-movement rider parsing failed") from exc


def strip_forced_movement_riders(text: str) -> str:
    """Remove only movement clauses fully represented by the universal schema."""
    try:
        clean = text
        while _FORCED.search(clean):
            clean, _, _ = parse_forced_movement_rider(clean)
        return clean
    except (TypeError, ValueError) as exc:
        raise ValueError("forced-movement rider stripping failed") from exc
