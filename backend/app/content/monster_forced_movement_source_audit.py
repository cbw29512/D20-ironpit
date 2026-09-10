from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def forced_movement_issues(attack: WeaponAttack, actions: str) -> list[str]:
    """Verify declarative push distance and target-size limits against SRD action text."""
    distance = attack.push_target_away_ft
    if distance <= 0:
        return []
    push = rf"push(?:es)?\s+the\s+target\s+up\s+to\s+{distance}\s*(?:ft\.?|feet)\s+straight\s+away"
    maximum = attack.push_target_max_size
    if maximum is None:
        matches = bool(re.search(push, actions, re.IGNORECASE))
    else:
        size_name = re.escape(maximum.value)
        matches = bool(re.search(rf"\b{size_name}\s+or\s+smaller\b[^.]*{push}", actions, re.IGNORECASE))
    return [] if matches else [f"push-rider-mismatch:{attack.id}"]
