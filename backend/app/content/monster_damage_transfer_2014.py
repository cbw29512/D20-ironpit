"""Source-verified 2014 Damage Transfer while grappling or attached.

Universal primitive: while the source is grappling a creature, half the damage
dealt to the source (rounded down) is transferred to that creature; the source
takes the remainder. Reuses apply_damage and grapple_sources. No name dispatch.
Attachment for Cloaker is a separate relation pending its own binding.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)
_HEADING = re.compile(
    r"<strong>(?P<name>[^<]+)\.</strong>(?P<body>.*?)(?=<strong>|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_DAMAGE_TRANSFER = re.compile(
    r"While (?:it is grappling a creature|attached to a creature), the [\w\s'-]+ takes only half the damage dealt to it(?: \(rounded down\))?, and (?:that creature|the creature grappled by the [\w\s'-]+) takes the other half\.",
    re.IGNORECASE,
)


def supports_damage_transfer_2014(monster: SourceMonster2014) -> str | None:
    """Return the trait name if the full printed clause is present."""
    try:
        source = monster.source_traits or ""
        for section in _HEADING.finditer(source):
            name = section.group("name").strip()
            if name not in monster.trait_names:
                continue
            if _DAMAGE_TRANSFER.search(section.group("body")):
                return name
        return None
    except Exception:
        logger.exception("Damage Transfer source proof failed for %s.", monster.id)
        raise
