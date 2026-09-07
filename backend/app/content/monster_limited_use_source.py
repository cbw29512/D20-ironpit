from __future__ import annotations

import re
from dataclasses import dataclass

from app.content.monster_combat_scope import base_feature_name

_FIELDS = ("traits", "actions", "bonusActions", "reactions")
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})
_MARKER = re.compile(r"\((?:[^)]*(?:Recharge\s+\d(?:\s*[-–]\s*\d)?|\d+\s*/\s*Day)[^)]*)\)", re.I)
_RECHARGE = re.compile(r"Recharge\s+(\d)(?:\s*[-–]\s*(\d))?", re.I)
_PER_DAY = re.compile(r"(\d+)\s*/\s*Day", re.I)


@dataclass(frozen=True)
class LimitedUseSpec:
    section: str
    heading: str
    base_name: str
    max_uses: int
    recharge_minimum: int | None = None
    recharge_maximum: int | None = None


def _is_heading(value: str) -> bool:
    base = re.sub(r"\s*\([^)]*\)$", "", value).strip()
    words = base.split()
    if not words or len(value) > 100:
        return False
    return all(word.lower() in _CONNECTORS or re.fullmatch(r"[A-Z][A-Za-z’'\-]*", word) for word in words)


def _limited_headings(source: object) -> list[str]:
    text = re.sub(r"\s+", " ", str(source or "")).strip()
    if not text:
        return []
    names: list[str] = []
    for sentence in re.split(r"(?<=\.)\s+", text):
        candidate = sentence[:-1].strip() if sentence.endswith(".") else ""
        if candidate and _MARKER.search(candidate):
            if not _is_heading(candidate):
                raise ValueError(f"Limited-use marker is not on a parseable heading: {candidate!r}")
            names.append(candidate)
    if _MARKER.search(text) and not names:
        raise ValueError(f"SRD limited-use heading could not be parsed from: {text!r}")
    return names


def parse_limited_use_names(row: dict[str, object]) -> list[str]:
    names: list[str] = []
    for field in _FIELDS:
        names.extend(f"{field}:{name}" for name in _limited_headings(row.get(field, "")))
    return names


def limited_use_spec(fingerprint: str) -> LimitedUseSpec:
    section, separator, heading = fingerprint.partition(":")
    if not separator or section not in _FIELDS:
        raise ValueError(f"Invalid limited-use fingerprint: {fingerprint!r}")
    per_day = _PER_DAY.search(heading)
    if per_day:
        return LimitedUseSpec(section, heading, base_feature_name(heading), int(per_day.group(1)))
    recharge = _RECHARGE.search(heading)
    if recharge:
        minimum = int(recharge.group(1)); maximum = int(recharge.group(2) or recharge.group(1))
        return LimitedUseSpec(section, heading, base_feature_name(heading), 1, minimum, maximum)
    raise ValueError(f"Limited-use fingerprint has no supported marker: {fingerprint!r}")
