from __future__ import annotations

import html
import re
import unicodedata

_TRAIT = re.compile(r"<strong>\s*Spellcasting\.\s*</strong>", re.I)
_LEVEL = re.compile(r"\b(\d+)(?:st|nd|rd|th)-level spellcaster\b", re.I)
_ABILITY = re.compile(r"spellcasting ability is (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)", re.I)
_SAVE_DC = re.compile(r"spell save DC\s*(\d+)", re.I)
_ATTACK_BONUS = re.compile(r"([+-]\d+) to hit with spell attacks", re.I)
_CANTRIPS = re.compile(r"Cantrips?\s*\(at will\)\s*:\s*(.+)", re.I)
_SLOTS = re.compile(r"(\d+)(?:st|nd|rd|th) level\s*\((\d+) slots?\)\s*:\s*(.+)", re.I)


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _spell_rows(source_traits: str) -> list[str]:
    rows = []
    for raw in re.findall(r"<(?:p|li)>(.*?)</(?:p|li)>", source_traits or "", re.I | re.S):
        text = _plain(raw)
        if _CANTRIPS.search(text) or _SLOTS.search(text):
            rows.append(text)
    return rows


def _names(value: str) -> list[str]:
    return [item.strip().strip(".*") for item in value.split(",") if item.strip().strip(".*")]


def parse_spellcasting(source_traits: str | None) -> dict | None:
    raw = source_traits or ""
    if not _TRAIT.search(raw):
        return None
    text = _plain(raw)
    level = _LEVEL.search(text); ability = _ABILITY.search(text)
    save_dc = _SAVE_DC.search(text); attack_bonus = _ATTACK_BONUS.search(text)
    if not level or not ability:
        return {"source_complete": False, "unsupported_text": "missing caster level or casting ability"}
    spells: list[dict] = []; slots: dict[str, int] = {}
    for row in _spell_rows(raw):
        cantrip = _CANTRIPS.search(row)
        if cantrip:
            spells.extend({"id": _slug(name), "name": name, "level": 0} for name in _names(cantrip.group(1)))
            continue
        match = _SLOTS.search(row)
        if match:
            spell_level, count, names = match.groups(); slots[spell_level] = int(count)
            spells.extend({"id": _slug(name), "name": name, "level": int(spell_level)} for name in _names(names))
    return {
        "caster_level": int(level.group(1)), "ability": ability.group(1).lower(),
        "save_dc": int(save_dc.group(1)) if save_dc else None,
        "attack_bonus": int(attack_bonus.group(1)) if attack_bonus else None,
        "slots": slots, "spells": spells, "source_complete": bool(spells),
        "unsupported_text": None if spells else "no printed spell rows parsed",
    }
