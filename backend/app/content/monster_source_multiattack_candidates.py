from __future__ import annotations

import logging
import re

from app.domain.capability_attacks import (
    AttackCapabilityDefinition,
    CapabilityActionSlot,
    MultiattackCapabilityDefinition,
    SaveCapabilityDefinition,
)

logger = logging.getLogger(__name__)
_MULTI_COUNT = re.compile(
    r"Multiattack\.\s+The\s+[^.]+?\s+makes\s+(one|two|three|four|five|six)\s+([A-Za-z’' -]+?)\s+attacks?\.",
    re.IGNORECASE,
)
_MULTI_GENERIC = re.compile(
    r"Multiattack\.\s+The\s+[^.]+?\s+makes\s+(one|two|three|four|five|six)\s+attacks?,\s+using\s+([^.]+?)\s+in any combination\.",
    re.IGNORECASE,
)
_MULTI_REPLACE_ONE = re.compile(
    r"Multiattack\.\s+The\s+[^.]+?\s+makes\s+(one|two|three|four|five|six)\s+([A-Za-z’' -]+?)\s+attacks?\.\s+"
    r"It can replace one attack with a use of ([A-Za-z’' -]+)\.",
    re.IGNORECASE,
)
_WORD_COUNT = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to slug multiattack value %r.", value)
        raise RuntimeError("Multiattack id could not be derived.") from exc


def source_multiattack(
    row: dict[str, object],
    attacks: list[AttackCapabilityDefinition],
    save_actions: list[SaveCapabilityDefinition],
) -> MultiattackCapabilityDefinition | None:
    try:
        text = str(row.get("actions", ""))
        replace = _MULTI_REPLACE_ONE.search(text)
        if replace:
            wanted = replace.group(2).strip().lower().rstrip("s")
            attack_ids = [
                item.id for item in attacks
                if item.name.lower().rstrip("s") == wanted
            ]
            save_name = replace.group(3).strip().lower()
            save_ids = [
                item.id for item in save_actions
                if item.name.lower() == save_name
            ]
            count = _WORD_COUNT[replace.group(1).lower()]
            if attack_ids and len(save_ids) == 1:
                return MultiattackCapabilityDefinition(
                    id=f"srd-{_slug(str(row['name']))}-multiattack",
                    slots=[
                        CapabilityActionSlot(
                            attack_ids=attack_ids,
                            save_action_ids=save_ids if index == 0 else [],
                        )
                        for index in range(count)
                    ],
                )

        match = _MULTI_COUNT.search(text)
        if match:
            wanted = match.group(2).strip().lower().rstrip("s")
            ids = [
                item.id for item in attacks
                if item.name.lower().rstrip("s") == wanted
            ]
            if ids:
                return MultiattackCapabilityDefinition(
                    id=f"srd-{_slug(str(row['name']))}-multiattack",
                    slots=[
                        CapabilityActionSlot(attack_ids=ids)
                        for _ in range(_WORD_COUNT[match.group(1).lower()])
                    ],
                )

        match = _MULTI_GENERIC.search(text)
        if match:
            ids = [
                item.id for item in attacks
                if re.search(rf"\b{re.escape(item.name)}\b", match.group(2), re.IGNORECASE)
            ]
            if ids:
                return MultiattackCapabilityDefinition(
                    id=f"srd-{_slug(str(row['name']))}-multiattack",
                    slots=[
                        CapabilityActionSlot(attack_ids=ids)
                        for _ in range(_WORD_COUNT[match.group(1).lower()])
                    ],
                )
        return None
    except Exception as exc:
        logger.exception("Failed to compile source Multiattack for %r.", row.get("name"))
        raise RuntimeError("Source Multiattack could not be compiled.") from exc
