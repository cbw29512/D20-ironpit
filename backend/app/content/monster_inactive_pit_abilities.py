"""Printed abilities that stay on the card but are INACTIVE in the Pit.

Chris lock: an ability that does not change combat math (damage, to-hit, AC,
saves, HP, conditions, action economy) remains printed, is marked INACTIVE,
and must not block certification. Data stays on the monster for later use.
Only park an ability when it actually changes combat math and lacks a primitive.
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_RECHARGE = re.compile(r"\s*\((?:Recharge\s+\d(?:\s*[-–]\s*\d)?|\d+\s*/\s*Day)[^)]*\)\s*$", re.I)

# Form / disguise: the creature fights in its natural / true form.
INACTIVE_PIT_FORM_TRAITS = frozenset({
    "Shapechanger",
    "Adhesive (Object Form Only)",
    "False Appearance (Object Form Only)",
})
INACTIVE_PIT_FORM_ACTIONS = frozenset({
    "Change Shape",
    "Illusory Appearance",
})

# Telepathy, senses, communication, and insight.
INACTIVE_PIT_COMMUNICATION_TRAITS = frozenset({
    "Limited Telepathy",
    "Telepathic Bond",
    "Probing Telepathy",
    "Shark Telepathy",
    "Divine Awareness",
    "Inscrutable",
    "Shielded Mind",
    "Sense Magic",
    "Speak with Beasts and Plants",
    "Speak with Beasts",
    "Speak with Plants",
    "Ethereal Sight",
    "Blind Senses",
    "Echolocation",
})
INACTIVE_PIT_COMMUNICATION_ACTIONS = frozenset({
    "Read Thoughts",
})

# Environment / appearance / post-fight flavor. The standard Pit is arena-neutral.
INACTIVE_PIT_ENVIRONMENT_TRAITS = frozenset({
    "False Appearance",
    "Rejuvenation",
    "Hellish Rejuvenation",
    "Siege Monster",
    "Incorporeal Movement",
    "Web Sense",
    "Web Walker",
    "Mimicry",
    "Antimagic Susceptibility",
    "Immutable Form",
    "Lair Actions",
    "Regional Effects",
    "Create Spawn",
    "Elemental Demise",
    "Amphibious",
    "Limited Amphibiousness",
    "Spider Climb",
    "Water Breathing",
    "Hold Breath",
    "Keen Hearing",
    "Keen Hearing and Smell",
    "Keen Hearing and Sight",
    "Keen Sight",
    "Keen Sight and Smell",
    "Keen Smell",
})

INACTIVE_PIT_UTILITY_ACTIONS = frozenset({
    "Create Food and Water",
    "Speak with Beasts and Plants",
})

INACTIVE_PIT_TRAITS = (
    INACTIVE_PIT_FORM_TRAITS
    | INACTIVE_PIT_COMMUNICATION_TRAITS
    | INACTIVE_PIT_ENVIRONMENT_TRAITS
)
INACTIVE_PIT_ACTIONS = (
    INACTIVE_PIT_FORM_ACTIONS
    | INACTIVE_PIT_COMMUNICATION_ACTIONS
    | INACTIVE_PIT_UTILITY_ACTIONS
)


def ability_base_name(name: str) -> str:
    return _RECHARGE.sub("", str(name or "")).strip()


def is_inactive_pit_trait(name: str) -> bool:
    """True when a printed trait stays on the card but must not block READY."""
    try:
        return ability_base_name(name) in INACTIVE_PIT_TRAITS
    except Exception:
        logger.exception("Failed to classify inactive Pit trait %r.", name)
        raise


def is_inactive_pit_action(name: str) -> bool:
    """True when a printed action is form/utility/summon flavor and must not block."""
    try:
        label = ability_base_name(name)
        folded = label.casefold()
        if label in INACTIVE_PIT_ACTIONS or folded in {item.casefold() for item in INACTIVE_PIT_ACTIONS}:
            return True
        return folded.startswith(("summon", "conjure", "children of the night"))
    except Exception:
        logger.exception("Failed to classify inactive Pit action %r.", name)
        raise


def inactive_pit_names(*groups: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    """Preserve printed names that the Pit marks INACTIVE."""
    try:
        found: list[str] = []
        for group in groups:
            for name in group:
                if is_inactive_pit_trait(name) or is_inactive_pit_action(name):
                    found.append(name)
        return tuple(found)
    except Exception:
        logger.exception("Failed to collect inactive Pit ability names.")
        raise
