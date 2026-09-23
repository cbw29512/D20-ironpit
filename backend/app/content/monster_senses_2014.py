from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.senses import CombatSenses

logger = logging.getLogger(__name__)
_SENSES = ("darkvision", "blindsight", "truesight", "tremorsense")


def parse_combat_senses_2014(monster: SourceMonster2014) -> CombatSenses:
    """Convert the pinned SRD senses text into source-neutral combat data."""
    try:
        text = monster.senses or ""
        ranges: dict[str, int] = {}
        for sense in _SENSES:
            match = re.search(rf"\b{sense}\s+(\d+)\s*ft\.?", text, re.IGNORECASE)
            ranges[f"{sense}_ft"] = int(match.group(1)) if match else 0
        blindsight = ranges["blindsight_ft"]
        blind_beyond = (
            blindsight
            if blindsight and re.search(r"blind\s+beyond\s+this\s+radius", text, re.IGNORECASE)
            else None
        )
        return CombatSenses(
            **ranges,
            blind_beyond_ft=blind_beyond,
            blindsight_requires_hearing=(
                blindsight > 0 and "Echolocation" in monster.trait_names
            ),
        )
    except Exception as exc:
        logger.exception("Failed to parse 2014 senses for %s.", monster.name)
        raise RuntimeError(f"2014 senses could not be parsed for {monster.id}.") from exc
