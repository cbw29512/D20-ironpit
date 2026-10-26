"""Arena-neutral source proof for audible alarm reactions without effects.

The standard Pit has no creatures to summon from off-board and no noise-triggered
combat state. Preserve printed text, never invent damage, a save, or a reaction
resource cost. Any additional printed mechanical rider remains a blocker.
"""
from __future__ import annotations

import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

_ALERT_ONLY = re.compile(
    r"When bright light or a creature is within (?P<trigger>\d+) feet of the "
    r"(?P<actor>[\w -]+), it emits a shriek audible within (?P<audible>\d+) "
    r"feet of it\. The (?P=actor) continues to shriek until the disturbance "
    r"moves out of range and for (?P<dice>\d+d\d+) of the (?P=actor)'s "
    r"turns afterward\.",
    re.IGNORECASE,
)


def arena_inert_audible_alert_reactions_2014(
    monster: SourceMonster2014,
) -> frozenset[str]:
    """Recognize complete source-owned alerts; do not allow hidden riders."""
    sections = source_sections_2014(
        monster.source_reactions, include_continuations=True,
    )
    permitted: set[str] = set()
    for name in monster.reaction_names:
        printed = sections.get(name)
        match = _ALERT_ONLY.fullmatch(printed or "")
        if match is None:
            continue
        if (match["actor"].casefold() != monster.name.casefold()
                or int(match["trigger"]) != 30
                or int(match["audible"]) != 300
                or match["dice"] != "1d4"):
            continue
        permitted.add(name)
    return frozenset(permitted)
