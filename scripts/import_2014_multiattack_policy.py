from __future__ import annotations

import re
from collections.abc import Callable

AttackIds = Callable[[str, list[dict]], list[str]]
_SUBJECT = r"(?:the [a-z][a-z -]*? )?"


def parse_policy_multiattack(text: str, attacks: list[dict], ids_for_label: AttackIds) -> dict | None:
    capped = re.fullmatch(
        _SUBJECT + r"makes (two|three|four) attacks, only one of which can be (?:a|an|its|his|her) ([a-z][a-z -]*?) attack\. ?",
        text,
        re.I,
    )
    if capped:
        counts = {"two": 2, "three": 3, "four": 4}
        capped_ids = ids_for_label(capped.group(2), attacks)
        all_ids = [attack["id"] for attack in attacks]
        if len(capped_ids) == 1 and all_ids:
            return {
                "id": "multiattack", "name": "Multiattack",
                "slots": [all_ids[:] for _ in range(counts[capped.group(1).lower()])],
                "policy": {"at_most_once_attack_ids": capped_ids},
            }

    hit_follow_up = re.fullmatch(
        _SUBJECT + r"makes one attack with (?:its|his|her) ([a-z][a-z -]*?)\. "
        r"if that attack hits, (?:the [a-z -]+|it) can make one ([a-z][a-z -]*?) attack against the same target\. ?",
        text,
        re.I,
    )
    if hit_follow_up:
        first = ids_for_label(hit_follow_up.group(1), attacks)
        second = ids_for_label(hit_follow_up.group(2), attacks)
        if first and second:
            return {
                "id": "multiattack", "name": "Multiattack", "slots": [first, second],
                "policy": {
                    "requires_previous_hit_slots": [1],
                    "same_target_as_previous_slots": [1],
                },
            }

    distinct = re.fullmatch(
        _SUBJECT + r"makes two melee attacks, each one with a different weapon\.?",
        text,
        re.I,
    )
    if distinct:
        ids = [attack["id"] for attack in attacks if attack["kind"] == "melee"]
        if len(ids) >= 2:
            return {
                "id": "multiattack", "name": "Multiattack", "slots": [ids[:], ids[:]],
                "policy": {"distinct_attack_ids": True},
            }

    repeated = re.fullmatch(
        _SUBJECT + r"makes 1d(\d+) ([a-z][a-z -]*?) attacks?\. ?",
        text,
        re.I,
    )
    if repeated:
        ids = ids_for_label(repeated.group(2), attacks)
        if ids:
            return {
                "id": "multiattack", "name": "Multiattack", "slots": [ids],
                "policy": {
                    "repeat_slot_index": 0,
                    "repeat_dice_count": 1,
                    "repeat_dice_size": int(repeated.group(1)),
                },
            }
    return None