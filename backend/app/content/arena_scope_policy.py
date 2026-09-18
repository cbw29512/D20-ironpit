from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

_DISABLED_ACTION_PATTERNS = (
    re.compile(r"\b(?:summon|conjure|spawn|split|duplicate|animate)\b", re.I),
    re.compile(r"\b(?:teleport|plane shift|dimension door|misty step|ethereal(?:ness| stride| jaunt)?)\b", re.I),
    re.compile(r"\b(?:banish|banishment)\b", re.I),
)
_DISABLED_EQUIPMENT_ACTIONS = frozenset({"Antennae"})
_ARENA_OUT_OF_SCOPE_TRAITS = frozenset({
    "Confer Fire Resistance", "Corrode Metal", "Detect Life", "Divine Awareness",
    "Earth Glide", "Elemental Demise", "Ethereal Jaunt", "False Appearance",
    "False Appearance (Object Form Only)", "Faultless Tracker", "Hellish Rejuvenation",
    "Hellish Restoration", "Incorporeal Movement", "Inscrutable", "Iron Scent",
    "Limited Telepathy", "Mimicry", "Misty Escape", "Probing Telepathy", "Rejuvenation",
    "Rust Metal", "Sense Magic", "Shielded Mind", "Siege Monster",
    "Speak with Beasts and Plants", "Telepathic Bond", "Treasure Sense", "Tree Stride",
    "Underwater Camouflage", "Web Sense", "Web Walker",
})
_EQUIPMENT_REFERENCE = re.compile(
    r"\b(?:armor|armour|shield|weapon|equipment|object(?:s)?(?: made of)? metal|metal object(?:s)?)\b", re.I,
)
_EQUIPMENT_DEGRADATION = re.compile(
    r"\b(?:corrod\w*|rust\w*|dissolv\w*|destroy\w*|permanent\w*|cumulative|penalty)\b", re.I,
)
_CREATURE_EFFECT = re.compile(
    r"\b(?:saving throw|escape dc|hit points?|target takes|creature takes|grappled|restrained|poisoned|"
    r"blinded|stunned|prone|frightened|paralyzed|unconscious|swallowed)\b", re.I,
)


def action_key(value: str) -> str:
    try:
        clean = re.sub(r"\s*\(Recharge\s+[^)]+\)", "", value, flags=re.I).rstrip(".")
        clean = re.sub(r"\s*\(\d+\s*/\s*Day\)", "", clean, flags=re.I).rstrip(".")
        return re.sub(r"[^a-z0-9]+", "-", clean.lower()).strip("-")
    except Exception:
        logger.exception("Failed to normalize arena action key for %r.", value)
        raise


def is_arena_disabled_action(name: str) -> bool:
    try:
        return name in _DISABLED_EQUIPMENT_ACTIONS or any(
            pattern.search(name) is not None for pattern in _DISABLED_ACTION_PATTERNS
        )
    except Exception:
        logger.exception("Failed to classify arena action %r.", name)
        raise


def is_arena_out_of_scope_trait(name: str) -> bool:
    try:
        return name in _ARENA_OUT_OF_SCOPE_TRAITS
    except Exception:
        logger.exception("Failed to classify arena trait %r.", name)
        raise


def is_arena_disabled_attack_detail(text: str | None) -> bool:
    try:
        if not text:
            return False
        return bool(
            _EQUIPMENT_REFERENCE.search(text)
            and _EQUIPMENT_DEGRADATION.search(text)
            and not _CREATURE_EFFECT.search(text)
        )
    except Exception:
        logger.exception("Failed to classify arena attack detail %r.", text)
        raise
