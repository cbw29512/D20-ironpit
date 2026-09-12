from __future__ import annotations

import re
from collections.abc import Callable

AttackIds = Callable[[str, list[dict]], list[str]]
SequenceParser = Callable[[str, list[dict]], list[list[str]] | None]


def _merge(sequences: list[list[list[str]]]) -> list[list[str]]:
    slots: list[list[str]] = []
    for index in range(max(len(sequence) for sequence in sequences)):
        choices: list[str] = []
        for sequence in sequences:
            if index >= len(sequence):
                continue
            for attack_id in sequence[index]:
                if attack_id not in choices:
                    choices.append(attack_id)
        if choices:
            slots.append(choices)
    return slots


def alternatives(
    text: str, attacks: list[dict], ids_for_label: AttackIds,
    sequence: SequenceParser, numbers: dict[str, int],
) -> list[list[str]] | None:
    parts = re.split(r"\.\s+(?:Or|Alternatively)\s+", text, flags=re.I)
    if len(parts) < 2:
        parts = re.split(
            r"\s+or\s+(?=(?:it\s+)?(?:can\s+)?(?:use|uses|makes)\b)",
            text, maxsplit=1, flags=re.I,
        )
    if len(parts) < 2:
        return None
    sequences = [sequence(part, attacks) for part in parts]
    if any(item is None for item in sequences):
        return None
    return _merge([item for item in sequences if item is not None])


def inline_count_alternative(
    text: str, attacks: list[dict], ids_for_label: AttackIds,
    sequence: SequenceParser, numbers: dict[str, int],
) -> list[list[str]] | None:
    words = "|".join(numbers)
    match = re.search(
        rf"^(.*?)(?:\s+or\s+)({words}) with (?:its|his|her) ([a-z][a-z -]*?)\.?$",
        text, re.I,
    )
    if match:
        left = sequence(match.group(1), attacks)
        ids = ids_for_label(match.group(3), attacks)
        if left and ids:
            return _merge([left, [ids[:] for _ in range(numbers[match.group(2).lower()])]])
    typed = re.search(
        rf"makes ({words}) (melee|ranged) attacks? or ({words}) (melee|ranged) attacks?\.?$",
        text, re.I,
    )
    if not typed:
        return None
    sequences: list[list[list[str]]] = []
    for count_word, kind in ((typed.group(1), typed.group(2)), (typed.group(3), typed.group(4)):
        ids = [attack["id"] for attack in attacks if attack["kind"] == kind.lower()]
        if not ids:
            return None
        sequences.append([ids[:] for _ in range(numbers[count_word.lower()])])
    return _merge(sequences)


def replacement(
    text: str, attacks: list[dict], ids_for_label: AttackIds,
    numbers: dict[str, int],
) -> list[list[str]] | None:
    words = "|".join(numbers)
    base = re.search(
        rf"makes ({words}) attacks?,? either with (?:its|his|her) ([a-z][a-z -]*?) "
        r"or (?:its|his|her) ([a-z][a-z -]*?)\.", text, re.I,
    )
    replace = re.search(r"replace one of those attacks with (?:a|an) ([a-z][a-z -]*?) attack", text, re.I)
    if not base or not replace:
        return None
    ids = ids_for_label(f"{base.group(2)} or {base.group(3)}", attacks)
    replacement_ids = ids_for_label(replace.group(1), attacks)
    if not ids or not replacement_ids:
        return None
    slots = [ids[:] for _ in range(numbers[base.group(1).lower()])]
    slots[0] = [*slots[0], *replacement_ids]
    return slots


def medusa_style(
    text: str, attacks: list[dict], ids_for_label: AttackIds,
    listed: SequenceParser, numbers: dict[str, int],
) -> list[list[str]] | None:
    words = "|".join(numbers)
    match = re.search(
        rf"makes either ({words}) melee attacks--(.+?)--or ({words}) ranged attacks with "
        r"(?:its|his|her) ([a-z][a-z -]*?)\.?$", text, re.I,
    )
    if not match:
        return None
    left = listed(f"makes {match.group(1)} attacks: {match.group(2)}.", attacks)
    ids = ids_for_label(match.group(4), attacks)
    if not left or not ids:
        return None
    right = [ids[:] for _ in range(numbers[match.group(3).lower()])]
    return _merge([left, right])


def apply_any_replacement(
    text: str, slots: list[list[str]] | None, attacks: list[dict], ids_for_label: AttackIds,
) -> list[list[str]] | None:
    if not slots:
        return None
    match = re.search(r"can use ([a-z][a-z -]*?) in place of any melee attack", text, re.I)
    if not match:
        return slots
    replacement_ids = ids_for_label(match.group(1), attacks)
    if not replacement_ids:
        return None
    return [
        [*slot, *[attack_id for attack_id in replacement_ids if attack_id not in slot]]
        for slot in slots
    ]
