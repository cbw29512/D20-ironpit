from __future__ import annotations

import re
from collections.abc import Callable

AttackIds = Callable[[str, list[dict]], list[str]]
_SUBJECT = r"(?:the [a-z][a-z -]*? )?"
_COUNTS = {"two": 2, "three": 3, "four": 4}


def _best_attack_id(attack_ids: list[str], attacks: list[dict]) -> str | None:
    """Choose the strongest source variant without introducing monster-name logic."""
    candidates = [attack for attack in attacks if attack.get("id") in set(attack_ids)]
    if not candidates:
        return None
    return max(candidates, key=lambda attack: (attack.get("damage", {}).get("average", 0), -attacks.index(attack)))["id"]


def parse_policy_multiattack(text: str, attacks: list[dict], ids_for_label: AttackIds) -> dict | None:
    range_choice_substitution = re.fullmatch(
        _SUBJECT + r"makes two ([a-z][a-z -]*?) attacks? or two ([a-z][a-z -]*?) attacks?\. "
        r"(?:it|he|she) can use (?:its|his|her) ([a-z][a-z -]*?) in place of one ([a-z][a-z -]*?) attack\. ?",
        text, re.I,
    )
    if range_choice_substitution:
        first_label, second_label, substitute_label, replaced_label = range_choice_substitution.groups()
        first = ids_for_label(first_label, attacks); second = ids_for_label(second_label, attacks)
        substitute = ids_for_label(substitute_label, attacks); replaced = ids_for_label(replaced_label, attacks)
        if first and second and len(substitute) == 1 and frozenset(replaced) in {frozenset(first), frozenset(second)}:
            melee = first if set(replaced) == set(first) else second
            ranged = second if set(replaced) == set(first) else first
            melee_id = _best_attack_id(melee, attacks); ranged_id = _best_attack_id(ranged, attacks)
            if melee_id and ranged_id:
                return {
                    "id": "multiattack", "name": "Multiattack",
                    "slots": [[substitute[0], ranged_id], [melee_id, ranged_id]],
                }

    capped = re.fullmatch(
        _SUBJECT + r"makes (two|three|four) attacks, only one of which can be (?:with )?(?:a|an|its|his|her) ([a-z][a-z -]*?)(?: attack)?\. ?",
        text,
        re.I,
    )
    if capped:
        capped_ids = ids_for_label(capped.group(2), attacks)
        all_ids = [attack["id"] for attack in attacks]
        if len(capped_ids) == 1 and all_ids:
            return {
                "id": "multiattack", "name": "Multiattack",
                "slots": [all_ids[:] for _ in range(_COUNTS[capped.group(1).lower()])],
                "policy": {"at_most_once_attack_ids": capped_ids},
            }

    drawn_extra = re.fullmatch(
        _SUBJECT + r"makes (two|three|four) ([a-z][a-z -]*?) attacks?\. "
        r"if (?:it|he|she) has (?:a|an|its|his|her) ([a-z][a-z -]*?) drawn, "
        r"(?:it|he|she) can also make (?:a|an|one) ([a-z][a-z -]*?) attack\. ?",
        text,
        re.I,
    )
    if drawn_extra:
        primary = ids_for_label(drawn_extra.group(2), attacks)
        drawn = ids_for_label(drawn_extra.group(3), attacks)
        extra = ids_for_label(drawn_extra.group(4), attacks)
        if primary and extra and set(drawn) == set(extra):
            return {
                "id": "multiattack", "name": "Multiattack",
                "slots": [primary[:] for _ in range(_COUNTS[drawn_extra.group(1).lower()])] + [extra],
            }

    form_choice = re.fullmatch(
        r"in ([a-z][a-z -]*?) form, " + _SUBJECT + r"makes (two|three|four) ([a-z][a-z -]*?) attacks?\. "
        r"in ([a-z][a-z -]*?) form, (?:it|he|she) makes (two|three|four) ([a-z][a-z -]*?) attacks?\. "
        r"in ([a-z][a-z -]*?) form, (?:it|he|she) can attack like (?:a|an) ([a-z][a-z -]*?) or (?:a|an) ([a-z][a-z -]*?)\. ?",
        text,
        re.I,
    )
    if form_choice:
        first_form, first_count, first_label, second_form, second_count, second_label, _, like_first, like_second = form_choice.groups()
        first = ids_for_label(first_label, attacks); second = ids_for_label(second_label, attacks)
        same_count = _COUNTS[first_count.lower()] == _COUNTS[second_count.lower()]
        referenced_forms = {like_first.lower(), like_second.lower()} == {first_form.lower(), second_form.lower()}
        if first and second and same_count and referenced_forms:
            choices = list(dict.fromkeys([*first, *second])); count = _COUNTS[first_count.lower()]
            return {"id": "multiattack", "name": "Multiattack", "slots": [choices[:] for _ in range(count)],
                    "policy": {"same_attack_as_previous_slots": list(range(1, count))}}

    mixed_form_choice = re.fullmatch(
        r"in ([a-z][a-z -]*?) form, " + _SUBJECT + r"makes (two|three|four) ([a-z][a-z -]*?) attacks? or (two|three|four) ([a-z][a-z -]*?) attacks?\. "
        r"in ([a-z][a-z -]*?) form, (?:it|he|she) can attack like (?:a|an) ([a-z][a-z -]*?) or make (two|three|four) ([a-z][a-z -]*?) attacks?\. ?",
        text, re.I,
    )
    if mixed_form_choice:
        first_form, first_count, first_label, second_count, second_label, _, like_form, third_count, third_label = mixed_form_choice.groups()
        first = ids_for_label(first_label, attacks); second = ids_for_label(second_label, attacks); third = ids_for_label(third_label, attacks)
        counts = {_COUNTS[first_count.lower()], _COUNTS[second_count.lower()], _COUNTS[third_count.lower()]}
        if first and second and third and len(counts) == 1 and like_form.lower() == first_form.lower():
            choices = list(dict.fromkeys([*first, *second, *third])); count = counts.pop()
            return {"id": "multiattack", "name": "Multiattack", "slots": [choices[:] for _ in range(count)],
                    "policy": {"same_attack_as_previous_slots": list(range(1, count))}}

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
