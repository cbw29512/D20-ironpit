from __future__ import annotations

import hashlib
import re

from app.content.monster_trait_source_audit import parse_trait_names

_FIELDS = ("traits", "actions", "bonusActions", "reactions")
_CASTING = re.compile(r"\bSpellcasting\b|\bcast(?:s|ing)?\b", re.IGNORECASE)
_SPELL_GROUP = re.compile(
    r"\b(?:At Will|\d+/Day(?: Each)?):\s*(.*?)(?=\s+(?:At Will|\d+/Day(?: Each)?):|$)",
    re.IGNORECASE,
)
_SPELL_ACCESS_GROUP = re.compile(
    r"\b(At Will|\d+/Day(?: Each)?):\s*(.*?)(?=\s+(?:At Will|\d+/Day(?: Each)?):|$)",
    re.IGNORECASE,
)
_SPELL_SAVE_DC = re.compile(r"\bspell save DC\s*(\d+)\b", re.IGNORECASE)
_DIRECT_CAST = re.compile(
    r"\bcasts?\s+([A-Z][A-Za-z'’\- ]*?)(?=\s+on\b|\s+at\b|\s+using\b|\s+requiring\b|,|\.|\()"
)
_SOURCE_LIST_BOUNDARY_FIXES = {
    "Adult Gold Dragon": (
        "Zone of Truth Weakening Breath. Strength Saving Throw:",
        "Zone of Truth. Weakening Breath. Strength Saving Throw:",
    ),
}


def normalized(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _corrected_spell_text(row: dict[str, object], field: str) -> str:
    text = normalized(row.get(field, ""))
    fix = _SOURCE_LIST_BOUNDARY_FIXES.get(str(row.get("name", "")))
    if fix is not None:
        before, after = fix
        if before in text:
            text = text.replace(before, after, 1)
    return text


def spellcasting_source_text(row: dict[str, object]) -> str:
    chunks: list[str] = []
    for field in _FIELDS:
        text = normalized(row.get(field, ""))
        if text and _CASTING.search(text):
            chunks.append(f"{field}={text}")
    return "\n".join(chunks)


def spellcasting_fingerprint(row: dict[str, object]) -> str | None:
    text = spellcasting_source_text(row)
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None


def _outside_parentheses_prefix(text: str, headings: list[str]) -> str:
    markers = tuple(f" {heading}." for heading in headings)
    depth = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
            continue
        if char == ")" and depth:
            depth -= 1
            continue
        if depth:
            continue
        if any(text.startswith(marker, index) for marker in markers) or char == ".":
            return text[:index]
    return text


def _split_outside_parentheses(text: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    parts.append(text[start:].strip())
    return [part for part in parts if part]


def printed_spell_names(row: dict[str, object]) -> set[str]:
    spells: set[str] = set()
    for field in _FIELDS:
        text = _corrected_spell_text(row, field)
        if not text or not _CASTING.search(text):
            continue
        headings = parse_trait_names(text, preserve_annotations=True)
        for group in _SPELL_GROUP.findall(text):
            bounded = _outside_parentheses_prefix(group, headings)
            spells.update(_split_outside_parentheses(bounded))
    return spells


def base_spell_name(value: str) -> str:
    return re.sub(r"\s*\(.*\)\s*$", "", value).strip()


def source_spell_names(row: dict[str, object]) -> set[str]:
    spells = {base_spell_name(item) for item in printed_spell_names(row)}
    for field in _FIELDS:
        text = _corrected_spell_text(row, field)
        if not text or not _CASTING.search(text):
            continue
        spells.update(match.group(1).strip() for match in _DIRECT_CAST.finditer(text))
    return spells


def spell_save_dc(row: dict[str, object]) -> int:
    match = _SPELL_SAVE_DC.search(spellcasting_source_text(row))
    if match is None:
        raise ValueError(f"Spell save DC could not be parsed for {row.get('name')!r}.")
    return int(match.group(1))


def spell_daily_uses(row: dict[str, object], spell_name: str) -> int | None:
    """Return N for N/Day, None for At Will; fail closed if the selected spell is absent."""
    for field in _FIELDS:
        text = _corrected_spell_text(row, field)
        if not text or not _CASTING.search(text):
            continue
        headings = parse_trait_names(text, preserve_annotations=True)
        for label, group in _SPELL_ACCESS_GROUP.findall(text):
            bounded = _outside_parentheses_prefix(group, headings)
            names = {base_spell_name(item) for item in _split_outside_parentheses(bounded)}
            if spell_name not in names:
                continue
            if label.lower() == "at will":
                return None
            return int(label.split("/", 1)[0])
    raise ValueError(f"Selected spell {spell_name!r} is not present for {row.get('name')!r}.")
