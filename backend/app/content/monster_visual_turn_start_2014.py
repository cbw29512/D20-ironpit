"""2014 printed-source verification for reusable visual turn-start rules.

Only immutable source parameters are selected here; combat uses universal
visibility, saving throws, timed conditions and terminal effects.
"""
from __future__ import annotations

import logging
import re
from html import unescape

from app.domain.visual_turn_start import VisualTurnStartRule
from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)
_GAZE = "Petrifying Gaze"
_DC = re.compile(r"\bdc\s+(\d+)\s+constitution\b", re.IGNORECASE)
_RANGE = re.compile(r"\bwithin\s+(\d+)\s+feet\b", re.IGNORECASE)



def _source_clause_with_continuations(source: str, heading: str) -> str:
    """Read a printed section and adjacent unheaded paragraphs only.

    Unrelated named traits cannot satisfy missing source-proof clauses.
    This selects source content, never combat behavior.
    """
    try:
        active = False
        paragraphs: list[str] = []
        for raw in re.findall(r"<p\b[^>]*>(.*?)</p>", source, flags=re.I | re.S):
            named = re.search(r"<strong\b[^>]*>(.*?)</strong>", raw, flags=re.I | re.S)
            if named:
                label = unescape(re.sub(r"<[^>]+>", "", named.group(1))).strip().rstrip(".")
                if active:
                    break
                active = label == heading
            if active:
                paragraphs.append(" ".join(unescape(re.sub(r"<[^>]+>", "", raw)).split()))
        return " ".join(paragraphs).casefold()
    except Exception:
        logger.exception("Failed reading 2014 source clause %s", heading)
        raise

def visual_turn_start_rule_2014(monster: SourceMonster2014) -> VisualTurnStartRule | None:
    """Fail closed unless the actual source supports the whole visual-save policy."""
    try:
        if _GAZE not in monster.trait_names:
            return None
        source = monster.source_traits or ""
        printed = _source_clause_with_continuations(source, _GAZE)
        dc = _DC.search(printed)
        distance = _RANGE.search(printed)
        required = (
            "restrained", "petrified", "end of its next turn",
            "isn't incapacitated", "saving throw",
        )
        aversion = (
            ("avert its eyes" in printed)
            and ("can't see" in printed)
            and ("surprised" in printed)
            and ("immediately make the save" in printed)
        )
        if not (dc and distance and aversion and all(s in printed for s in required)):
            return None
        margin = 5 if "fails by 5 or more" in printed else None
        # A five-point failure margin must be source-proven to cause immediate
        # petrification, not inferred from the numeric phrase alone.
        if margin is not None and "instantly petrified" not in printed:
            return None
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
