"""Source provenance for generic 2014 on-hit ability-score loss.

Never classify a combatant by its name. Verify the immutable on-hit field
against the exact attack paragraph in the pinned printed source.
"""
from __future__ import annotations

import logging
import re
from html import unescape

from app.content.monster_attack_effect_validation_2014 import supported_ability_score_reduction_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014

logger = logging.getLogger(__name__)
_SCORE_CLAUSE = re.compile(
    r"the target['’]s\\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"
    r"\\s+score is reduced by\\s+(\\d+)d(\\d+)",
    re.IGNORECASE,
)


def _printed_reduction(monster: SourceMonster2014, attack: SourceAttack2014) -> dict | None:
    # A source action is an HTML paragraph. Keep only the named attack paragraph.
    for paragraph in re.findall(r"<p\\b[^>]*>(.*?)</p>", monster.source_actions or "", re.I | re.S):
        text = re.sub(r"<[^>]+>", "", unescape(paragraph))
        text = re.sub(r"\\s+", " ", text).strip()
        if not re.match(rf"^{re.escape(attack.name)}\\.", text, re.IGNORECASE):
            continue
        match = _SCORE_CLAUSE.search(text)
        if match is None:
            return None
        return {"ability": match.group(1).lower(), "dice_count": int(match.group(2)),
                "dice_size": int(match.group(3))}
    return None


def source_proves_ability_score_reduction_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> bool:
    """Require the source action and compiled parameters to agree exactly."""
    try:
        printed = _printed_reduction(monster, attack)
        row = attack.on_hit_ability_score_reduction
        if printed is None:
            return row is None
        return supported_ability_score_reduction_2014(row) and row == printed
    except Exception:
        logger.exception("2014 attack ability-score source proof failed: %s", attack.id)
        raise
