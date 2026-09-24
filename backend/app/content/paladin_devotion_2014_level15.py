from __future__ import annotations

import logging

from app.domain.passive_modifiers import PassiveModifierGrant

logger = logging.getLogger(__name__)

_PROTECTED_TYPES = ["aberration", "celestial", "elemental", "fey", "fiend", "undead"]


def purity_of_spirit_2014() -> list[PassiveModifierGrant]:
    """Compile Purity of Spirit as permanent Protection from Evil and Good defenses."""
    try:
        return [
            PassiveModifierGrant(
                source_id="purity-of-spirit",
                source_name="Purity of Spirit",
                kind="attacks-against-disadvantage",
                source_creature_types=list(_PROTECTED_TYPES),
            ),
            PassiveModifierGrant(
                source_id="purity-of-spirit",
                source_name="Purity of Spirit",
                kind="condition-immunity",
                condition_id="charmed",
                source_creature_types=list(_PROTECTED_TYPES),
            ),
            PassiveModifierGrant(
                source_id="purity-of-spirit",
                source_name="Purity of Spirit",
                kind="condition-immunity",
                condition_id="frightened",
                source_creature_types=list(_PROTECTED_TYPES),
            ),
        ]
    except Exception:
        logger.exception("Failed to compile 2014 Purity of Spirit passive modifiers.")
        raise
