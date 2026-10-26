"""Semantic roster scan for failed-save conditions with start-turn damage."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_SEMANTIC = re.compile(
    r"saving throw or become (?P<condition>\w+)\. While \w+ in this way, "
    r"the target can't regain hit points, and it takes \d+ \(\d+d\d+\) "
    r"\w+ damage at the start of each of its turns\. The \w+ target can "
    r"repeat the saving throw at the end of each of its turns, ending the "
    r"effect on itself on a success\.",
    re.IGNORECASE,
)


def semantic_start_turn_damage_names_2014(
    monster: SourceMonster2014,
) -> tuple[str, ...]:
    """Find candidates by printed behavior, never monster or ability identity."""
    try:
        sections = source_sections_2014(monster.source_actions)
        return tuple(
            name
            for name, text in sections.items()
            if _SEMANTIC.search(" ".join(text.replace("’", "'").split()))
        )
    except Exception:
        logger.exception(
            "Failed start-turn damage-condition semantic scan for %s.",
            monster.id,
        )
        raise
