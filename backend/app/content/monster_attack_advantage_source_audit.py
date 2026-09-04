from __future__ import annotations

import logging
import re

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)

_TARGET_MISSING_HP = "target_missing_hit_points"
_MISSING_HP_ADVANTAGE = re.compile(
    r"\bAdvantage\b[^.]{0,240}\bdoesn[’']t have all (?:its|their) Hit Points\b",
    re.IGNORECASE,
)


def _source_has_missing_hp_advantage(row: dict[str, object]) -> bool:
    try:
        source = "\n".join((
            str(row.get("traits", "")),
            str(row.get("actions", "")),
        ))
        return bool(_MISSING_HP_ADVANTAGE.search(source))
    except Exception:
        logger.exception("Failed to inspect SRD missing-HP attack Advantage text.")
        raise


def attack_advantage_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> list[str]:
    """Fail closed when SRD and runtime disagree on target-missing-HP Advantage."""
    try:
        source_has = _source_has_missing_hp_advantage(row)
        runtime_has = _TARGET_MISSING_HP in template.attack_roll_advantage_triggers
        issues: list[str] = []
        if source_has and not runtime_has:
            issues.append("attack-advantage-runtime-missing:target-missing-hit-points")
        elif runtime_has and not source_has:
            issues.append("attack-advantage-source-missing:target-missing-hit-points")
        return issues
    except Exception:
        logger.exception("Attack Advantage source audit failed for %s.", template.id)
        raise
