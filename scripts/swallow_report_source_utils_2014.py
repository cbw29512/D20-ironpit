"""Shared source-text and diagnostic helpers for the 2014 Swallow/Engulf audit."""
from __future__ import annotations
import re
from app.content.monster_source_sections_2014 import source_sections_2014

_SEMANTIC = re.compile(r"\b(?:swallow(?:s|ed)?|engulf(?:s|ed)?)\b", re.I)


def source_text(monster) -> str:
    sections = source_sections_2014(monster.source_actions, include_continuations=True)
    selected = [text for heading, text in sections.items()
                if _SEMANTIC.search(heading) or _SEMANTIC.search(text)]
    return " ".join(" ".join(text.split()) for text in selected)


def is_relevant(printed: str) -> bool:
    return bool(_SEMANTIC.search(printed)
                and "blinded" in printed.casefold()
                and "restrained" in printed.casefold())


def incompatibility(monster) -> str:
    if not monster.swallow_actions:
        return "missing_structured_source_parameters"
    data = monster.swallow_actions[0]
    if data.get("attack_id") is None or data.get("start_turn_save_dc") is not None:
        return "engulf_start_turn_save_profile_not_supported"
    if data.get("requires_existing_grapple") is False:
        return "failed_save_on_bite_profile_unproven"
    if data.get("regurgitation_damage_threshold") is not None:
        return "damage_threshold_regurgitation_profile_not_supported"
    return "source_profile_not_supported"
