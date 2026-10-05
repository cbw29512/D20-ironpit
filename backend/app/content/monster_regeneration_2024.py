from __future__ import annotations

import logging
import re

from app.domain.regeneration import RegenerationTrait
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_REGEN = re.compile(
    r"\bRegeneration\.\s+The\s+\w+\s+regains\s+(\d+)\s+Hit Points at the start of each of its turns"
    r"( if it has at least 1 Hit Point)?\.",
    re.I,
)
_SUPPRESS = re.compile(
    r"If the \w+ takes ([A-Za-z]+) or ([A-Za-z]+) damage, this trait doesn[’']t function on the \w+[’']s next turn\.",
    re.I,
)
_ZERO_LIFE = re.compile(
    r"The \w+ dies only if it starts its turn with 0 Hit Points and doesn[’']t regenerate\.",
    re.I,
)


def regeneration_trait_2024(source_traits: object) -> RegenerationTrait | None:
    """Compile a printed 2024 Regeneration trait into the universal lifecycle primitive."""
    try:
        text = str(source_traits or "")
        if "Regeneration." not in text:
            return None
        match = _REGEN.search(text)
        if match is None:
            raise ValueError("Printed 2024 Regeneration has an unsupported source form.")
        suppression = _SUPPRESS.search(text)
        suppressed: list[DamageType] = []
        if suppression is not None:
            suppressed = [DamageType(suppression.group(1).lower()), DamageType(suppression.group(2).lower())]
        survives = bool(_ZERO_LIFE.search(text))
        if survives != bool(suppression):
            raise ValueError("2024 Regeneration suppression/zero-HP lifecycle must be source-complete.")
        return RegenerationTrait(
            amount=int(match.group(1)),
            requires_positive_hp=bool(match.group(2)),
            suppressed_by_damage_types=suppressed,
            survives_zero_until_turn=survives,
            source_name="Regeneration",
        )
    except Exception:
        logger.exception("Failed to compile 2024 Regeneration source.")
        raise
