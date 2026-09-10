from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def _matches(actions: str, phrase: str, maximum) -> bool:
    if maximum is None:
        return bool(re.search(phrase, actions, re.IGNORECASE))
    size_name = re.escape(maximum.value)
    return bool(re.search(rf"\b{size_name}\s+or\s+smaller\b[^.]*{phrase}", actions, re.IGNORECASE))


def forced_movement_issues(attack: WeaponAttack, actions: str) -> list[str]:
    """Verify declarative forced-movement distance and target-size limits against SRD text."""
    issues: list[str] = []
    push = attack.push_target_away_ft
    if push > 0:
        phrase = rf"push(?:es)?\s+the\s+target\s+up\s+to\s+{push}\s*(?:ft\.?|feet)\s+straight\s+away"
        if not _matches(actions, phrase, attack.push_target_max_size):
            issues.append(f"push-rider-mismatch:{attack.id}")
    pull = attack.pull_target_toward_ft
    if pull > 0:
        phrase = rf"pull(?:s)?\s+the\s+target\s+up\s+to\s+{pull}\s*(?:ft\.?|feet)\s+(?:straight\s+)?toward"
        if not _matches(actions, phrase, attack.pull_target_max_size):
            issues.append(f"pull-rider-mismatch:{attack.id}")
    return issues