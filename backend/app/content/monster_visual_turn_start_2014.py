"""2014 printed-source verification for reusable visual turn-start rules.

Only immutable source parameters are selected here; combat uses universal
visibility, saving throws, timed conditions and terminal effects.
"""
from __future__ import annotations

import logging
import re

from app.combat.turn_start_visual_policy import VisualTurnStartRule
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)
_GAZE = "Petrifying Gaze"
_DC = re.compile(r"\bdc\s+(\d+)\s+constitution\b", re.IGNORECASE)
_RANGE = re.compile(r"\bwithin\s+(\d+)\s+feet\b", re.IGNORECASE)


def visual_turn_start_rule_2014(monster: SourceMonster2014) -> VisualTurnStartRule | None:
    """Fail closed unless the actual source supports the whole visual-save policy."""
    try:
        if _GAZE not in monster.trait_names:
            return None
        source = monster.source_traits or ""
        sections = source_sections_2014(source)
        printed = sections.get(_GAZE, "").casefold()
        full = source.casefold()
        dc = _DC.search(printed)
        distance = _RANGE.search(printed)
        required = (
            "restrained", "petrified", "end of its next turn",
            "isn't incapacitated", "saving throw",
        )
        aversion = (
            ("avert its eyes" in full)
            and ("can't see" in full)
            and ("surprised" in full)
            and ("immediately make the save" in full)
        )
        if not (dc and distance and aversion and all(s in printed for s in required)):
            return None
        margin = 5 if "fails by 5 or more" in printed else None
        return VisualTurnStartRule(
            source_id="petrifying-gaze",
            source_name=_GAZE,
            range_ft=int(distance.group(1)),
            save_dc=int(dc.group(1)),
            save_ability="constitution",
            immediate_petrification_margin=margin,
        )
    except Exception:
        logger.exception("2014 visual source verification failed for %s", monster.id)
        raise
