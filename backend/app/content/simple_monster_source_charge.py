from __future__ import annotations

import re

_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"
_DICE = r"(?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?"
_RUNUP = re.compile(
    r"\b(?:the\s+)?[A-Za-z][A-Za-z'’ -]*\s+moved\s+(?P<distance>\d+)\+\s*feet\s+"
    r"straight\s+toward\s+(?:it|the\s+target)\s+immediately\s+before\s+the\s+hit\b",
    re.I,
)
_TARGET_SIZE = re.compile(
    rf"\bIf\s+(?:the\s+)?target\s+is\s+(?:a\s+)?(?P<size>{_SIZE})\s+or\s+smaller(?:\s+creature)?\s+and\s*$",
    re.I,
)
_EXTRA_DAMAGE = re.compile(
    rf"\bthe\s+target\s+takes\s+an\s+extra\s+\d+\s*\(\s*{_DICE}\s*\)\s+"
    r"(?P<damage_type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder)\s+damage\b",
    re.I,
)
_REPLACEMENT = re.compile(
    rf"\bor\s+\d+\s*\(\s*{_DICE}\s*\)\s+"
    r"(?P<damage_type>Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder)\s+damage\s+if\s+"
    r"(?:the\s+)?[A-Za-z][A-Za-z'’ -]*\s+moved\s+(?P<distance>\d+)\+\s*feet\s+straight\s+toward\s+the\s+target\s+"
    r"immediately\s+before\s+the\s+hit\b",
    re.I,
)
_PRONE = re.compile(r"\b(?:the\s+)?target\s+(?:also\s+)?has\s+the\s+Prone\s+condition\b", re.I)


def _damage(match: re.Match[str]) -> dict[str, object]:
    bonus = int(match.group("bonus") or 0)
    if match.group("sign") == "-":
        bonus *= -1
    return {
        "dice_count": int(match.group("count")),
        "dice_size": int(match.group("size")),
        "damage_bonus": bonus,
        "damage_type": match.group("damage_type").lower(),
    }


def parse_attack_charge(block: str) -> dict[str, object] | None:
    """Parse source-neutral run-up attack math into declarative Charge data."""
    replacement = _REPLACEMENT.search(block)
    if replacement is not None:
        return {
            "minimum_move_ft": int(replacement.group("distance")),
            "replacement_damage": _damage(replacement),
        }

    runup = _RUNUP.search(block)
    if runup is None:
        return None
    prefix = block[:runup.start()]
    suffix = block[runup.end():]
    size_match = _TARGET_SIZE.search(prefix)
    max_size = size_match.group("size").lower() if size_match is not None else None
    extra = _EXTRA_DAMAGE.search(suffix)
    prone = bool(_PRONE.search(suffix))
    if extra is None and not prone:
        return None

    charge: dict[str, object] = {"minimum_move_ft": int(runup.group("distance"))}
    if max_size is not None:
        charge["max_target_size"] = max_size
    if extra is not None:
        charge["bonus_damage"] = _damage(extra)
    if prone:
        if max_size is None:
            raise ValueError("Run-up Prone rider requires a source-proven maximum target size.")
        charge["prone_max_target_size"] = max_size
    return charge
