from __future__ import annotations

import html
import re
import unicodedata

ABILITIES = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _spell(value: str, usage: str, uses: int | None, shared_pool: bool) -> dict:
    clean = value.strip().rstrip(".")
    qualifier = None
    match = re.match(r"^(.*?)\s*\((.+)\)$", clean)
    if match:
        clean, qualifier = match.group(1).strip(), match.group(2).strip()
    return {
        "id": _slug(clean), "name": clean, "usage": usage,
        "uses_per_day": uses, "shared_pool": shared_pool, "qualifier": qualifier,
    }


def _header_metadata(text: str) -> tuple[str | None, int | None, int | None]:
    ability_match = re.search(r"spellcasting ability is (Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)", text, re.I)
    ability = ability_match.group(1).lower() if ability_match else None
    save_match = re.search(r"spell save DC\s*(\d+)", text, re.I)
    attack_match = re.search(r"([+\-]\d+) to hit with spell attacks", text, re.I)
    return ability, int(save_match.group(1)) if save_match else None, int(attack_match.group(1)) if attack_match else None


def _standard_groups(paragraphs: list[str], start: int) -> tuple[list[dict], int]:
    spells: list[dict] = []
    index = start + 1
    while index < len(paragraphs):
        raw = paragraphs[index]
        if re.search(r"<strong>", raw, re.I):
            break
        text = _plain(raw)
        match = re.match(r"^(At will|([1-9])/day( each)?):\s*(.+)$", text, re.I)
        if not match:
            break
        at_will = match.group(1).lower() == "at will"
        uses = None if at_will else int(match.group(2))
        each = bool(match.group(3))
        values = [item.strip() for item in match.group(4).split(",") if item.strip()]
        shared = not at_will and not each and len(values) > 1
        spells.extend(_spell(item, "at_will" if at_will else "per_day", uses, shared) for item in values)
        index += 1
    return spells, index


def parse_innate_spellcasting(source_traits: str | None) -> dict | None:
    if not re.search(r"Innate Spellcasting", source_traits or "", re.I):
        return None
    paragraphs = re.findall(r"<p>(.*?)</p>", source_traits or "", re.I | re.S)
    for index, raw in enumerate(paragraphs):
        header = _plain(raw)
        if not re.search(r"Innate Spellcasting", header, re.I):
            continue
        ability, save_dc, attack_bonus = _header_metadata(header)
        single = re.search(r"Innate Spellcasting\.\s*\((\d+)/Day\).*?cast\s+([^,]+)", header, re.I)
        if single:
            ability = ability or _header_metadata(header)[0]
            spell_rows = [_spell(single.group(2), "per_day", int(single.group(1)), False)]
        else:
            spell_rows, _ = _standard_groups(paragraphs, index)
        if ability in ABILITIES and spell_rows:
            return {
                "ability": ability, "save_dc": save_dc, "attack_bonus": attack_bonus,
                "spells": spell_rows, "source_complete": True, "unsupported_text": None,
            }
        return {
            "ability": ability or "charisma", "save_dc": save_dc, "attack_bonus": attack_bonus,
            "spells": spell_rows, "source_complete": False,
            "unsupported_text": header or _plain(source_traits),
        }
    return {
        "ability": "charisma", "spells": [], "source_complete": False,
        "unsupported_text": _plain(source_traits),
    }
