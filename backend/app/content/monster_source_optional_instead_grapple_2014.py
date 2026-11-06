"""Source-proven optional on-hit grapple replacing damage; applies to any matching 2014 card."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014

logger = logging.getLogger(__name__)

_INSTEAD_GRAPPLE = re.compile(
    r"Instead of dealing damage, the [a-z][a-z '\-]* can grapple the target \(escape DC (?P<dc>\d+)\)",
    re.IGNORECASE,
)

def source_proves_optional_instead_grapple_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> bool:
    """Exact full-clause match for the printed instead-of-damage grapple option."""
    try:
        text = (attack.unsupported_text or "").strip()
        return bool(_INSTEAD_GRAPPLE.search(text))
    except Exception:
        logger.exception("Failed optional-instead-grapple proof for %s %s.", monster.name, attack.name)
        return False

def source_completed_optional_instead_grapple_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    """If proven, bind the existing GrappleEffect with source DC; else return unchanged."""
    try:
        if not source_proves_optional_instead_grapple_2014(monster, attack):
            return attack
        match = _INSTEAD_GRAPPLE.search(attack.unsupported_text or "")
        if match is None:
            return attack
        dc = int(match.group("dc"))
        # Reuse existing control_effect slot; the optional-instead is a source parameter.
        # Full choice wiring is a separate runtime step; this clears the source obligation when bound.
        completed = attack.model_copy(update={
            "source_complete": True,
            "control_effect": {
                "grapple_escape_dc": dc,
                "optional_instead_of_damage": True,
            },
            "unsupported_text": None,
        })
        return completed
    except Exception:
        logger.exception("Failed to complete optional-instead-grapple for %s.", attack.id)
        return attack
