from __future__ import annotations

import re
from collections.abc import Callable

AttackIds = Callable[[str, list[dict]], list[str]]


def parse_policy_multiattack(text: str, attacks: list[dict], ids_for_label: AttackIds) -> dict | None:
    hit_follow_up = re.fullmatch(
        r"makes one attack with (?:its|his|her) ([a-z][a-z -]*?)\. "
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

    distinct = re.fullmatch(r"makes two melee attacks, each one with a different weapon\.?", text, re.I)
    if distinct:
        ids = [attack["id"] for attack in attacks if attack["kind"] == "melee"]
        if len(ids) >= 2:
            return {
                "id": "multiattack", "name": "Multiattack", "slots": [ids[:], ids[:]],
                "policy": {"distinct_attack_ids": True},
            }

    repeated = re.fullmatch(r"makes 1d(\d+) ([a-z][a-z -]*?) attacks?\.?", text, re.I)
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
