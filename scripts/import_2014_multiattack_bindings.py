from __future__ import annotations

import logging
import re
import unicodedata
from collections.abc import Callable

logger = logging.getLogger(__name__)
AttackIds = Callable[[str, list[dict]], list[str]]
_COUNTS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
_WORDS = "|".join(_COUNTS)
_LABEL = r"[a-z][a-z -]*?"
_SIZE = r"Tiny|Small|Medium|Large|Huge|Gargantuan"


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _refs(label: str, attacks: list[dict], ids_for_label: AttackIds) -> list[str]:
    refs: list[str] = []
    for choice in re.split(r"\s+or\s+", label, flags=re.I):
        clean = re.sub(r"^(?:its|his|her)\s+", "", choice.strip(), flags=re.I)
        ids = ids_for_label(clean, attacks)
        if not ids:
            ids = ids_for_label(f"{clean}s", attacks)
        candidates = ids or [_slug(clean)]
        for action_id in candidates:
            if action_id and action_id not in refs:
                refs.append(action_id)
    return refs


def _slots(action_ids: list[str], count_word: str) -> list[dict]:
    return [{"action_ids": action_ids[:]} for _ in range(_COUNTS[count_word.lower()])]


def parse_multiattack_binding(text: str, attacks: list[dict], ids_for_label: AttackIds) -> dict | None:
    """Bind source-level Multiattack references without claiming unresolved actions are executable."""
    try:
        dynamic = re.fullmatch(
            rf"the .+? makes as many ({_LABEL}) attacks? as (?:it|he|she) has ({_LABEL})\.?",
            text,
            re.I,
        )
        if dynamic:
            return {
                "slots": [{"action_ids": _refs(dynamic.group(1), attacks, ids_for_label)}],
                "repeat_slot_index": 0,
                "repeat_count_source": _slug(dynamic.group(2)),
            }

        replacement = re.fullmatch(
            rf"the .+? makes ({_WORDS}) ({_LABEL}) attacks?, each of which (?:it|he|she) can replace with one use of ({_LABEL})\.?",
            text,
            re.I,
        )
        if replacement:
            choices = _refs(replacement.group(2), attacks, ids_for_label)
            for action_id in _refs(replacement.group(3), attacks, ids_for_label):
                if action_id not in choices:
                    choices.append(action_id)
            return {"slots": _slots(choices, replacement.group(1))}

        all_hit_follow_up = re.fullmatch(
            rf"the .+? makes ({_WORDS}) ({_LABEL}) attacks?\. if both attacks hit a ({_SIZE}) or smaller (?:target|creature), "
            rf"(?:the target|the creature|it) is grappled \(escape DC (\d+)\), and .+? uses (?:its|his|her) ({_LABEL}) on (?:it|him|her)\.?",
            text,
            re.I,
        )
        if all_hit_follow_up and _COUNTS[all_hit_follow_up.group(1).lower()] == 2:
            return {
                "slots": _slots(_refs(all_hit_follow_up.group(2), attacks, ids_for_label), all_hit_follow_up.group(1)),
                "follow_up_action_id": _refs(all_hit_follow_up.group(5), attacks, ids_for_label)[0],
                "follow_up_condition": "all_attacks_hit_same_target",
                "follow_up_max_target_size": all_hit_follow_up.group(3).lower(),
                "follow_up_grapple_escape_dc": int(all_hit_follow_up.group(4)),
            }

        grapple_extra = re.fullmatch(
            rf"the .+? makes ({_WORDS}) ({_LABEL}) attacks?\. if .+? is grappling a creature, .+? can also use (?:its|his|her) ({_LABEL}) once\.?",
            text,
            re.I,
        )
        if grapple_extra:
            slots = _slots(_refs(grapple_extra.group(2), attacks, ids_for_label), grapple_extra.group(1))
            slots.append({
                "action_ids": _refs(grapple_extra.group(3), attacks, ids_for_label),
                "optional": True,
                "requirement": "source_has_grappled_target",
            })
            return {"slots": slots}

        available_extra = re.fullmatch(
            rf"the .+? makes ({_WORDS}) ({_LABEL}) attack and, if (?:it|he|she) can, uses (?:its|his|her) ({_LABEL})\.?",
            text,
            re.I,
        )
        if available_extra:
            slots = _slots(_refs(available_extra.group(2), attacks, ids_for_label), available_extra.group(1))
            slots.append({
                "action_ids": _refs(available_extra.group(3), attacks, ids_for_label),
                "optional": True,
                "requirement": "action_available",
            })
            return {"slots": slots}

        pair = re.fullmatch(
            rf"the .+? makes two attacks?: one with (?:its|his|her) ({_LABEL}) and one with (?:its|his|her) ({_LABEL}(?: or {_LABEL})?)\.?",
            text,
            re.I,
        )
        if pair:
            return {"slots": [
                {"action_ids": _refs(pair.group(1), attacks, ids_for_label)},
                {"action_ids": _refs(pair.group(2), attacks, ids_for_label)},
            ]}
        return None
    except Exception:
        logger.exception("Failed to parse generic 2014 Multiattack binding: %s", text)
        raise
