from __future__ import annotations

import re

# These actions only Hide/Disengage or alter pre-contact movement under the
# documented flat, no-Hide, no-kiting, initiative-opener arena abstraction.
ARENA_NEUTRAL_BONUS_ACTIONS = frozenset({
    "Aquatic Charge",
    "Charge",
    "Leap",
    "Nimble Escape",
    "Shadow Stealth",
})


def bonus_action_base_name(name: str) -> str:
    return re.sub(r"\s*\([^)]*\)$", "", name).strip()


def is_arena_neutral_bonus_action(name: str) -> bool:
    return bonus_action_base_name(name) in ARENA_NEUTRAL_BONUS_ACTIONS
