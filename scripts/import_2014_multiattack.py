from __future__ import annotations

import html
import re

from import_2014_multiattack_policy import parse_policy_multiattack
from import_2014_multiattack_variants import (
    alternatives,
    apply_any_replacement,
    inline_count_alternative,
    medusa_style,
    replacement,
    simple_patterns,
)

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
USE_COUNTS = {"once": 1, "twice": 2, "three times": 3, "four times": 4}


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
        return [attack["id"] for attack in attacks if _key(attack["name"]) == wanted[:-1]]
    return []


def _ids_for_label(label: str, attacks: list[dict]) -> list[str]:
    ids: list[str] = []
    for choice in re.split(r"\s+or\s+", label, flags=re.I):
        clean = re.sub(r"^(?:its|his|her)\s+", "", choice.strip(), flags=re.I)
        for attack_id in _ids_for_name(clean, attacks):
            if attack_id not in ids:
                ids.append(attack_id)
    return ids


def _repeated_named(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) ([a-z][a-z -]*?) attacks?\.?$", text, re.I)
    if not match:
        return None
    count = NUMBER_WORDS[match.group(1).lower()]; label = match.group(2).strip()
    ids = [attack["id"] for attack in attacks if attack["kind"] == label.lower()] if label.lower() in {"melee", "ranged"} else _ids_for_label(label, attacks)
    return [ids[:] for _ in range(count)] if ids else None


def _repeated_with(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) attacks? with (?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I)
    if not match:
        return None
    ids = _ids_for_label(match.group(2), attacks)
    return [ids[:] for _ in range(NUMBER_WORDS[match.group(1).lower()])] if ids else None


def _use_repeated(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"(?:it\s+)?(?:can\s+)?uses? (?:its\s+)?([a-z][a-z -]*?) (once|twice|three times|four times)\.?$", text, re.I)
    if not match:
        return None
    ids = _ids_for_label(match.group(1), attacks)
    return [ids[:] for _ in range(USE_COUNTS[match.group(2).lower()])] if ids else None


def _typed_with(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) (melee|ranged) attacks? with (?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I)
    if not match:
        return None
    kind = match.group(2).lower()
    ids = [attack_id for attack_id in _ids_for_label(match.group(3), attacks) if next(item for item in attacks if item["id"] == attack_id)["kind"] == kind]
    return [ids[:] for _ in range(NUMBER_WORDS[match.group(1).lower()])] if ids else None


def _listed(text: str, attacks: list[dict]) -> list[list[str]] | None:
    declared = re.search(r"makes (one|two|three|four|five|six|seven)(?: (?:melee|ranged))? attacks?:", text, re.I)
    if not declared:
        return None
    total = NUMBER_WORDS[declared.group(1).lower()]
    pieces = re.findall(r"(one|two|three|four|five|six|seven) (?:(?:with (?:its|his|her) )|to )([a-z][a-z -]*?)(?=,| and |\.|$)", text, re.I)
    slots: list[list[str]] = []
    for count_word, label in pieces:
        ids = _ids_for_label(label, attacks)
        if not ids:
            return None
        slots.extend([ids[:] for _ in range(NUMBER_WORDS[count_word.lower()])])
    return slots if len(slots) == total else None


def _generic_count(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) attacks?\.?$", text, re.I)
    if not match or not attacks:
        return None
    ids = [attack["id"] for attack in attacks]
    return [ids[:] for _ in range(NUMBER_WORDS[match.group(1).lower()])]


def _sequence(text: str, attacks: list[dict]) -> list[list[str]] | None:
    return _listed(text, attacks) or _typed_with(text, attacks) or _repeated_with(text, attacks) or _repeated_named(text, attacks) or _use_repeated(text, attacks) or _generic_count(text, attacks)


def parse_multiattack(source_actions: str | None, attacks: list[dict]) -> dict | None:
    for paragraph in re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S):
        if not re.search(r"<strong>\s*Multiattack", paragraph, re.I):
            continue
        text = re.sub(r"^Multiattack\.\s*", "", _plain(paragraph), flags=re.I)
        policy = parse_policy_multiattack(text, attacks, _ids_for_label)
        if policy is not None:
            return policy
        slots = (
            medusa_style(text, attacks, _ids_for_label, _listed, NUMBER_WORDS)
            or replacement(text, attacks, _ids_for_label, NUMBER_WORDS)
            or alternatives(text, attacks, _ids_for_label, _sequence, NUMBER_WORDS)
            or inline_count_alternative(text, attacks, _ids_for_label, _sequence, NUMBER_WORDS)
            or simple_patterns(text, attacks, _ids_for_label, NUMBER_WORDS)
            or _sequence(text, attacks)
        )
        slots = apply_any_replacement(text, slots, attacks, _ids_for_label)
        if slots:
            return {"id": "multiattack", "name": "Multiattack", "slots": slots}
        return None
    return None
