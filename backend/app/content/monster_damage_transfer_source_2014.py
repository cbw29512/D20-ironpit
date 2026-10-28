"""Source proof for 2014 Damage Transfer traits.

Verifies exact printed wording for Cloaker and Rug of Smothering.
No runtime dispatch on names. Foundation only; does not admit monsters.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_DAMAGE_TRANSFER_CLAUSES = {
    "Cloaker": (
        "While attached to a creature, the cloaker takes only half the damage dealt to it "
        "(rounded down), and that creature takes the other half."
    ),
    "Rug of Smothering": (
        "While it is grappling a creature, the rug takes only half the damage dealt to it, "
        "and the creature grappled by the rug takes the other half."
    ),
}


def source_proves_damage_transfer_2014(monster: SourceMonster2014) -> bool:
    """Return True only when the printed Damage Transfer clause matches exactly."""
    try:
        if "Damage Transfer" not in monster.trait_names:
            return False
        expected = _DAMAGE_TRANSFER_CLAUSES.get(monster.name)
        if expected is None:
            return False
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Damage Transfer")
        if printed is None:
            return False
        normalized = " ".join(printed.casefold().split())
        return normalized == " ".join(expected.casefold().split())
    except Exception:
        logger.exception("Damage Transfer source proof failed for %s.", monster.name)
        raise
