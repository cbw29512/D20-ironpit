from __future__ import annotations

import logging

from app.content.monk_open_hand_2014_audit_support import monk_feature_audit
from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def build_monk_2014_endgame_audits(level: int) -> list[FeatureAudit]:
    try:
        audits: list[FeatureAudit] = []
        if level >= 17:
            audits.append(monk_feature_audit(
                "quivering-palm", "Quivering Palm", "subclass",
                notes=(
                    "Uses the universal hit-armed deferred save-effect capability: 3 Ki on an "
                    "Unarmed Strike hit, then the next legal Action while the target remains marked. "
                    "Constitution save; failure reduces true HP to 0, success deals 10d10 necrotic damage."
                ),
            ))
        if level >= 18:
            audits.append(monk_feature_audit(
                "empty-body", "Empty Body", "class",
                notes=(
                    "Uses the universal timed self-buff action: Action + 4 Ki, applies the universal "
                    "Invisible condition and source-owned resistance to every supported damage type "
                    "except Force for 10 rounds."
                ),
            ))
        if level >= 19:
            audits.append(monk_feature_audit(
                "ability-score-improvement-l19",
                "Ability Score Improvement (+1 Wisdom, +1 Strength)",
                "class",
                notes="Canonical progression raises Wisdom 19 to 20 and Strength 13 to 14.",
            ))
        if level >= 20:
            audits.append(monk_feature_audit(
                "perfect-self", "Perfect Self", "class",
                notes=(
                    "Uses the universal initiative resource-refill capability: when initiative is "
                    "rolled with 0 Ki, regain 4 Ki without exceeding the resource maximum."
                ),
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Monk endgame audits at level %s.", level)
        raise
