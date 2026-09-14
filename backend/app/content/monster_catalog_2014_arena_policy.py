from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Iron Pit arena policy is universal. These names describe mechanics that remain
# preserved in source provenance but cannot execute inside the pocket dimension.
_ARENA_DISABLED_ACTION_PATTERNS = (
    re.compile(r"\b(?:summon|conjure|spawn|split|duplicate|animate)\b", re.I),
    re.compile(r"\b(?:teleport|plane shift|dimension door|misty step|ethereal(?:ness)?)\b", re.I),
    re.compile(r"\b(?:banish|banishment)\b", re.I),
    re.compile(r"\bwall of ice\b", re.I),
    re.compile(r"\billusory appearance\b", re.I),
    re.compile(
        r"^(?:Enslave|Possession|Nightmare Haunting|Phantasms|Read Thoughts|Heart Sight|"
        r"Children of the Night|Create Specter|Create Food and Water|Ink Cloud)(?:\s*\(|$)",
        re.I,
    ),
)
_ARENA_DISABLED_EQUIPMENT_ACTIONS = frozenset({"Antennae"})
_EQUIPMENT_REFERENCE = re.compile(
    r"\b(?:armor|armour|shield|weapon|equipment|object(?:s)?(?: made of)? metal|metal object(?:s)?)\b", re.I,
)
_EQUIPMENT_DEGRADATION = re.compile(
    r"\b(?:corrod\w*|rust\w*|dissolv\w*|destroy\w*|permanent\w*|cumulative|penalty)\b", re.I,
)
_CREATURE_EFFECT = re.compile(
    r"\b(?:saving throw|escape dc|hit points?|target takes|creature takes|grappled|restrained|poisoned|"
    r"blinded|stunned|prone|frightened|paralyzed|unconscious|swallowed)\b",
    re.I,
)
_WEAPON_QUALIFIED_DEFENSE = re.compile(
    r"\b(?:nonmagical attacks?|magic(?:al)? weapons?|silvered|adamantine|wielded by .* creatures?)\b",
    re.I,
)

# These traits are preserved as source truth but cannot alter an Iron Pit result
# under the universal pocket-dimension rules. They therefore never block a card.
ARENA_OUT_OF_SCOPE_TRAITS_2014 = frozenset({
    "Adhesive (Object Form Only)",
    "Confer Fire Resistance",
    "Corrode Metal",
    "Detect Life",
    "Divine Awareness",
    "Earth Glide",
    "Elemental Demise",
    "Ethereal Jaunt",
    "False Appearance",
    "False Appearance (Object Form Only)",
    "Faultless Tracker",
    "Hellish Rejuvenation",
    "Hellish Restoration",
    "Incorporeal Movement",
    "Inscrutable",
    "Iron Scent",
    "Limited Telepathy",
    "Mimicry",
    "Misty Escape",
    "Mucous Cloud",
    "Probing Telepathy",
    "Rejuvenation",
    "Rust Metal",
    "Sense Magic",
    "Shielded Mind",
    "Siege Monster",
    "Speak with Beasts and Plants",
    "Sunlight Weakness",
    "Telepathic Bond",
    "Treasure Sense",
    "Tree Stride",
    "Tunneler",
    "Underwater Camouflage",
    "Web Sense",
    "Web Walker",
})

# These remain usable source mechanics, but the existing movement engine already
# carries their only meaningful arena consequence. They must not be treated as
# disabled simply because the Pit prevents unreachable wall/altitude states.
ARENA_USABLE_MOVEMENT_TRAITS_2014 = frozenset({"Spider Climb"})


def is_arena_disabled_action_2014(name: str) -> bool:
    """Return True only for actions explicitly disabled by Iron Pit arena policy."""
    try:
        return name in _ARENA_DISABLED_EQUIPMENT_ACTIONS or any(
            pattern.search(name) is not None for pattern in _ARENA_DISABLED_ACTION_PATTERNS
        )
    except Exception as exc:
        logger.exception("Failed to classify 2014 arena action %r.", name)
        raise ValueError(f"Could not classify 2014 arena action {name!r}.") from exc


def is_arena_disabled_attack_detail_2014(text: str | None) -> bool:
    """Ignore only residual attack text whose remaining effect is equipment degradation."""
    try:
        if not text:
            return False
        return bool(
            _EQUIPMENT_REFERENCE.search(text)
            and _EQUIPMENT_DEGRADATION.search(text)
            and not _CREATURE_EFFECT.search(text)
        )
    except Exception as exc:
        logger.exception("Failed to classify 2014 attack residual %r.", text)
        raise ValueError("Could not classify 2014 attack residual.") from exc


def is_arena_ignored_weapon_defense_2014(text: str) -> bool:
    """Ignore defenses whose only extra rule is a weapon material, magic, or wielder qualifier."""
    try:
        return _WEAPON_QUALIFIED_DEFENSE.search(text) is not None
    except Exception as exc:
        logger.exception("Failed to classify 2014 weapon-qualified defense %r.", text)
        raise ValueError("Could not classify 2014 weapon-qualified defense.") from exc


def usable_movement_speed_2014(mode: str, speed_ft: int) -> int:
    """Apply arena movement restrictions without mutating source monster data."""
    try:
        if speed_ft < 0:
            raise ValueError("Movement speed cannot be negative.")
        return 0 if mode == "burrow" else speed_ft
    except Exception as exc:
        logger.exception("Failed to apply Iron Pit movement policy to %s=%s.", mode, speed_ft)
        raise ValueError(f"Could not apply Iron Pit movement policy to {mode!r}.") from exc
