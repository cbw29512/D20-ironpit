from __future__ import annotations

import html
import re

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
USE_COUNTS = {"once": 1, "twice": 2, "three times": 3, "four times": 4}


def _plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _key(value: str) -> str:
    text = re.sub(r"\battacks?\b", "", value.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _ids_for_name(name: str, attacks: list[dict]) -> list[str]:
    wanted = _key(name); candidates = [attack["id"] for attack in attacks if _key(attack["name"]) == wanted]
    if candidates: return candidates
    if wanted.endswith("s"): candidates = [attack["id"] for attack in attacks if _key(attack["name"]) == wanted[:-1]]
    return candidates


def _ids_for_label(label: str, attacks: list[dict]) -> list[str]:
    ids: list[str] = []
    for choice in re.split(r"\s+or\s+", label, flags=re.I):
        for attack_id in _ids_for_name(choice.strip(), attacks):
            if attack_id not in ids: ids.append(attack_id)
    return ids


def _repeated_named(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) ([a-z][a-z -]*?) attacks?\.?$", text, re.I)
    if not match: return None
    count = NUMBER_WORDS[match.group(1).lower()]; label = match.group(2).strip()
    ids = [attack["id"] for attack in attacks if attack["kind"] == label.lower()] if label.lower() in {"melee", "ranged"} else _ids_for_label(label, attacks)
    return [ids[:] for _ in range(count)] if ids else None


def _repeated_with(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) attacks? with (?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I)
    if not match: return None
    ids = _ids_for_label(match.group(2), attacks); return [ids[:] for _ in range(NUMBER_WORDS[match.group(1).lower()])] if ids else None


def _use_repeated(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"(?:it\s+)?(?:can\s+)?uses? (?:its\s+)?([a-z][a-z -]*?) (once|twice|three times|four times)\.?$", text, re.I)
    if not match: return None
    ids = _ids_for_label(match.group(1), attacks); return [ids[:] for _ in range(USE_COUNTS[match.group(2).lower()])] if ids else None


def _typed_with(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) (melee|ranged) attacks? with (?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I)
    if not match: return None
    count = NUMBER_WORDS[match.group(1).lower()]; kind = match.group(2).lower()
    ids = [attack_id for attack_id in _ids_for_label(match.group(3), attacks) if next(item for item in attacks if item["id"] == attack_id)["kind"] == kind]
    return [ids[:] for _ in range(count)] if ids else None


def _listed(text: str, attacks: list[dict]) -> list[list[str]] | None:
    declared = re.search(r"makes (one|two|three|four|five|six|seven)(?: (?:melee|ranged))? attacks?:", text, re.I)
    if not declared: return None
    total = NUMBER_WORDS[declared.group(1).lower()]
    pieces = re.findall(r"(one|two|three|four|five|six|seven) (?:(?:with (?:its|his|her) )|to )([a-z][a-z -]*?)(?=,| and |\.|$)", text, re.I)
    slots: list[list[str]] = []
    for count_word, label in pieces:
        ids = _ids_for_label(label, attacks)
        if not ids: return None
        slots.extend([ids[:] for _ in range(NUMBER_WORDS[count_word.lower()])])
    return slots if len(slots) == total else None


def _generic_count(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six|seven) attacks?\.?$", text, re.I)
    if not match or not attacks: return None
    ids = [attack["id"] for attack in attacks]; return [ids[:] for _ in range(NUMBER_WORDS[match.group(1).lower()])]


def _sequence(text: str, attacks: list[dict]) -> list[list[str]] | None:
    return _listed(text, attacks) or _typed_with(text, attacks) or _repeated_with(text, attacks) or _repeated_named(text, attacks) or _use_repeated(text, attacks) or _generic_count(text, attacks)


def _merge_alternatives(sequences: list[list[list[str]]]) -> list[list[str]]:
    slots: list[list[str]] = []
    for index in range(max(len(sequence) for sequence in sequences)):
        choices: list[str] = []
        for sequence in sequences:
            if index < len(sequence):
                for attack_id in sequence[index]:
                    if attack_id not in choices: choices.append(attack_id)
        if choices: slots.append(choices)
    return slots


def _alternatives(text: str, attacks: list[dict]) -> list[list[str]] | None:
    parts = re.split(r"\.\s+(?:Or|Alternatively)\s+", text, flags=re.I)
    if len(parts) < 2: parts = re.split(r"\s+or\s+(?=(?:it\s+)?(?:can\s+)?(?:use|uses|makes)\b)", text, maxsplit=1, flags=re.I)
    if len(parts) < 2: return None
    sequences = [_sequence(part, attacks) for part in parts]
    return _merge_alternatives([item for item in sequences if item is not None]) if all(item is not None for item in sequences) else None


def _inline_count_alternative(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"^(.*?)(?:\s+or\s+)(one|two|three|four|five|six|seven) with (?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I)
    if match:
        left = _sequence(match.group(1), attacks); ids = _ids_for_label(match.group(3), attacks)
        if left and ids: return _merge_alternatives([left, [ids[:] for _ in range(NUMBER_WORDS[match.group(2).lower()])]])
    typed = re.search(r"makes (one|two|three|four|five|six|seven) (melee|ranged) attacks? or (one|two|three|four|five|six|seven) (melee|ranged) attacks?\.?$", text, re.I)
    if not typed: return None
    sequences = []
    for count_word, kind in ((typed.group(1), typed.group(2)), (typed.group(3), typed.group(4))):
        ids = [attack["id"] for attack in attacks if attack["kind"] == kind.lower()]
        if not ids: return None
        sequences.append([ids[:] for _ in range(NUMBER_WORDS[count_word.lower()])])
    return _merge_alternatives(sequences)


def _replacement(text: str, attacks: list[dict]) -> list[list[str]] | None:
    base = re.search(r"makes (one|two|three|four|five|six|seven) attacks?,? either with (?:its|his|her) ([a-z][a-z -]*?) or (?:its|his|her) ([a-z][a-z -]*?)\.", text, re.I)
    replace = re.search(r"replace one of those attacks with (?:a|an) ([a-z][a-z -]*?) attack", text, re.I)
    if base and replace:
        ids = _ids_for_label(f"{base.group(2)} or {base.group(3)}", attacks); replacement = _ids_for_label(replace.group(1), attacks)
        if ids and replacement:
            slots = [ids[:] for _ in range(NUMBER_WORDS[base.group(1).lower()])]; slots[0] = [*slots[0], *replacement]; return slots
    return None


def _medusa_style(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes either (one|two|three|four|five|six|seven) melee attacks--(.+?)--or (one|two|three|four|five|six|seven) ranged attacks with (?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I)
    if not match: return None
    left = _listed(f"makes {match.group(1)} attacks: {match.group(2)}.", attacks); ids = _ids_for_label(match.group(4), attacks)
    if not left or not ids: return None
    right = [ids[:] for _ in range(NUMBER_WORDS[match.group(3).lower()])]; return _merge_alternatives([left, right])


def _apply_any_replacement(text: str, slots: list[list[str]] | None, attacks: list[dict]) -> list[list[str]] | None:
    if not slots: return None
    match = re.search(r"can use ([a-z][a-z -]*?) in place of any melee attack", text, re.I)
    if not match: return slots
    replacement = _ids_for_label(match.group(1), attacks)
    if not replacement: return None
    return [[*slot, *[item for item in replacement if item not in slot]] for slot in slots]


def parse_multiattack(source_actions: str | None, attacks: list[dict]) -> dict | None:
    for paragraph in re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S):
        if not re.search(r"<strong>\s*Multiattack", paragraph, re.I): continue
        text = re.sub(r"^Multiattack\.\s*", "", _plain(paragraph), flags=re.I)
        slots = _medusa_style(text, attacks) or _replacement(text, attacks) or _alternatives(text, attacks) or _inline_count_alternative(text, attacks) or _sequence(text, attacks)
        slots = _apply_any_replacement(text, slots, attacks)
        if slots: return {"id": "multiattack", "name": "Multiattack", "slots": slots}
        return None
    return None
