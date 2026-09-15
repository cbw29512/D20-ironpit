from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def _max_size_present(actions: str, size: object) -> bool:
    value = getattr(size, "value", size)
    return bool(re.search(rf"\b{re.escape(str(value))}\s+or\s+smaller\b", actions, re.IGNORECASE))


def grapple_issues(attack: WeaponAttack, actions: str) -> list[str]:
    control = attack.control_effect
    if control is None or control.grapple_escape_dc is None:
        return []
    issues: list[str] = []
    if "grappled" not in actions or f"escape dc {control.grapple_escape_dc}" not in actions:
        issues.append(f"grapple-rider-mismatch:{attack.id}")
    if control.max_target_size is not None and not _max_size_present(actions, control.max_target_size):
        issues.append(f"grapple-size-mismatch:{attack.id}")
    if control.restrains_while_grappled and "restrained" not in actions:
        issues.append(f"restrained-rider-mismatch:{attack.id}")
    for condition in control.conditions_while_grappled:
        pattern = rf"\b{re.escape(condition)}\s+condition\s+until\s+the\s+grapple\s+ends\b"
        if not re.search(pattern, actions, re.IGNORECASE):
            issues.append(f"grapple-linked-condition-mismatch:{attack.id}:{condition}")
    return issues
