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


def _typed_with(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(
        r"makes (one|two|three|four|five|six) (melee|ranged) attacks? with (?:its|his|her) ([a-z][a-z -]*?)\.?$",
        text,
        re.I,
    )
    if not match:
        return None
    count = NUMBER_WORDS[match.group(1).lower()]
    kind = match.group(2).lower()
    ids = [attack_id for attack_id in _ids_for_name(match.group(3), attacks)
           if next(item for item in attacks if item["id"] == attack_id)["kind"] == kind]
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


def _generic_count(text: str, attacks: list[dict]) -> list[list[str]] | None:
    match = re.search(r"makes (one|two|three|four|five|six) attacks?\.?$", text, re.I)
    if not match or not attacks:
        return None
    count = NUMBER_WORDS[match.group(1).lower()]
    ids = [attack["id"] for attack in attacks]
    return [ids[:] for _ in range(count)]


def _sequence(text: str, attacks: list[dict]) -> list[list[str]] | None:
    return (
        _listed(text, attacks)
        or _typed_with(text, attacks)
        or _repeated_with(text, attacks)
        or _repeated_named(text, attacks)
        or _generic_count(text, attacks)
    )


def _alternatives(text: str, attacks: list[dict]) -> list[list[str]] | None:
    parts = re.split(r"\.\s+(?:Or|Alternatively)\s+", text, flags=re.I)
    if len(parts) < 2:
        return None
    sequences = [_sequence(part, attacks) for part in parts]
    if any(sequence is None for sequence in sequences):
        return None
    resolved = [sequence for sequence in sequences if sequence is not None]
    slots: list[list[str]] = []
    for index in range(max(len(sequence) for sequence in resolved)):
        choices: list[str] = []
        for sequence in resolved:
            if index >= len(sequence):
                continue
            for attack_id in sequence[index]:
                if attack_id not in choices:
                    choices.append(attack_id)
        if choices:
            slots.append(choices)
    return slots or None


def parse_multiattack(source_actions: str | None, attacks: list[dict]) -> dict | None:
    for paragraph in re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S):
        if not re.search(r"<strong>\s*Multiattack", paragraph, re.I):
            continue
        text = re.sub(r"^Multiattack\.\s*", "", _plain(paragraph), flags=re.I)

        alternatives = _alternatives(text, attacks)
        if alternatives:
            return {"id": "multiattack", "name": "Multiattack", "slots": alternatives}

        # Parse the actual attack sequence even when the paragraph also grants a separate
        # ability (for example Frightful Presence). That other ability remains its own
        # unsupported action until the engine models it; it must not hide the attacks.
        slots = _sequence(text, attacks)
        if slots:
            return {"id": "multiattack", "name": "Multiattack", "slots": slots}

        # Replacement wording changes which actions are legal in an existing slot, so
        # keep those fail-closed until the source substitution itself is structured.
        if re.search(r"\b(replace|instead)\b", text, re.I):
            return None
        return None
    return None
