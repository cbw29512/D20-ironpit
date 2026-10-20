"""Source-proof visible-ally conditional immunity without printed-name dispatch."""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.passive_modifiers import PassiveModifierGrant

logger = logging.getLogger(__name__)
_VISIBLE_ALLY = re.compile(
    r"The [\w '\-]+ can't be (?P<condition>frightened) while it can see "
    r"an allied creature within (?P<range>\d+) feet of it\.", re.IGNORECASE,
)


def visible_ally_immunity_grants_2014(monster: SourceMonster2014) -> list[PassiveModifierGrant]:
    """Require the entire printed clause; radius and label belong to the source."""
    try:
        grants = []
        for name, text in source_sections_2014(monster.source_traits).items():
            match = _VISIBLE_ALLY.fullmatch(text)
            if name not in monster.trait_names or match is None:
                continue
            grants.append(PassiveModifierGrant(
                source_id=re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-"),
                source_name=name, kind="condition-immunity",
                condition_id=match["condition"].casefold(),
                required_visible_active_ally_within_ft=int(match["range"]),
            ))
        return grants
    except Exception:
        logger.exception("Failed visible-ally immunity source proof for %s.", monster.id)
        raise
