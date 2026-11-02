from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_audible_alert_2014 import arena_inert_audible_alert_reactions_2014

logger = logging.getLogger(__name__)

# Arena rules forbid adding combatants. Identify exactly the printed reaction
# that creates two new creatures; the source retains its full original wording.
_SPLIT_OFFSPRING = re.compile(r"\bsplits? into two new\b", re.IGNORECASE)
_SPLIT_TRIGGER = re.compile(r"\blightning or slashing damage\b", re.IGNORECASE)


def arena_unavailable_reaction_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Source-verified reactions whose only outcome violates the no-spawn rule."""
    try:
        source = monster.source_reactions or ""
        inert = set(arena_inert_audible_alert_reactions_2014(monster))
        if _SPLIT_OFFSPRING.search(source) and _SPLIT_TRIGGER.search(source):
            inert.update(
                name for name in monster.reaction_names
                if name == "Split" and "<strong>Split.</strong>" in source
            )

        # No amulet system exists in the Pit. Printed amulet-dependent
        # Shield reaction cannot change a combat outcome.
        if monster.id == "shield-guardian" and "Shield" in monster.reaction_names:
            from app.content.monster_source_sections_2014 import source_sections_2014
            printed = source_sections_2014(
                monster.source_reactions, include_continuations=True
            ).get("Shield", "")
            expected = (
                "When a creature makes an attack against the wearer of the "
                "guardian's amulet, the guardian grants a +2 bonus to the "
                "wearer's AC if the guardian is within 5 feet of the wearer."
            )
            if printed == expected:
                inert.add("Shield")
        return frozenset(inert)
    except Exception:
        logger.exception("Failed arena reaction classification for %s.", monster.name)
        raise
