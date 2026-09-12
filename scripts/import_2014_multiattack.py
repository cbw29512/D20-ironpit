from __future__ import annotations

import html
import re

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def _plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _key(value: str) -> str:
    text = re.sub(r"\battacks?\b", "", value.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _ids_for_name(name: str, attacks: list[dict]) -> list[str]:
    wanted = _key(name)
    candidates = [attack["id"] for attack in attacks if _key(attack["name"]) == wanted]
    if candidates:
        return candidates
    if wanted.endswith("s"):
        candidates = [attack["id"] for attack in attacks if _key(attack["name"]) == wanted[:-1]]
    return candidates


def _repeated_named(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six) ([a-z][a-z -]*?) attacks?\.?$", text, re.I)
    if not match:
        return None
    count = NUMBER_WORDS[match.group(1).lower()]
    label = match.group(2).strip()
    if label.lower() in {"melee", "ranged"}:
        ids = [attack["id"] for attack in attacks if attack["kind"] == label.lower()]
    else:
        ids = _ids_for_name(label, attacks)
    return [ids[:] for _ in range(count)] if ids else None


def _repeated_with(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six) attacks? with (?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I)
    if not match:
        return None
    count = NUMBER_WORDS[match.group(1).lower()]
    ids = _ids_for_name(match.group(2), attacks)
    return [ids[:] for _ in range(count)] if ids else None


def _listed(text: str, attacks: list[dict]) -> list[list[str]] | None:
    declared = re.search(r"makes (one|two|three|four|five|six) attacks?:", text, re.I)
    if not declared:
        return None
    total = NUMBER_WORDS[declared.group(1).lower()]
    pieces = re.findall(r"(one|two|three|four|five|six) with (?:its|his|her) ([a-z][a-z -]*?)(?=,| and |\.|$)", text, re.I)
    slots: list[list[str]] = []
    for count_word, label in pieces:
        ids = _ids_for_name(label, attacks)
        if not ids:
            return None
        slots.extend([ids[:] for _ in range(NUMBER_WORDS[count_word.lower()])])
    return slots if len(slots) == total else None


def parse_multiattack(source_actions: str | None, attacks: list[dict]) -> dict | None:
    for paragraph in re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S):
        if not re.search(r"<strong>\s*Multiattack", paragraph, re.I):
            continue
        text = re.sub(r"^Multiattack\.\s*", "", _plain(paragraph), flags=re.I)
        if re.search(r"\b(alternatively|replace|instead|also| if |can use|uses? .+ twice| or )\b", f" {text.lower()} "):
            return None
        slots = _listed(text, attacks) or _repeated_with(text, attacks) or _repeated_named(text, attacks)
        if slots:
            return {"id": "multiattack", "name": "Multiattack", "slots": slots}
        generic = re.search(r"makes (one|two|three|four|five|six) attacks?\.?$", text, re.I)
        if generic and attacks:
            count = NUMBER_WORDS[generic.group(1).lower()]
            ids = [attack["id"] for attack in attacks]
            return {"id": "multiattack", "name": "Multiattack", "slots": [ids[:] for _ in range(count)]}
        return None
    return None
