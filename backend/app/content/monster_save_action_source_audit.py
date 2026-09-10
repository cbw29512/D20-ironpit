from __future__ import annotations

import re
from typing import Any

from app.content.monster_save_area_source_audit import area_save_issues
from app.content.monster_save_failure_source_audit import failure_effect_issues


def _dice_pattern(count: int, size: int, bonus: int) -> re.Pattern[str]:
    base = rf"{count}\s*d\s*{size}"
    if bonus == 0:
        return re.compile(base + r"(?:\s*\+\s*0)?", re.IGNORECASE)
    sign = r"\+" if bonus > 0 else "-"
    return re.compile(base + rf"\s*{sign}\s*{abs(bonus)}", re.IGNORECASE)


def _push_present(action: Any, actions: str) -> bool:
    if not action.push_target_away_ft:
        return True
    distance = action.push_target_away_ft
    pattern = rf"push(?:es|ed)?\s+(?:the\s+)?target\s+up\s+to\s+{distance}\s+(?:feet|ft\.?).*?straight\s+away"
    if not re.search(pattern, actions, re.IGNORECASE):
        return False
    if action.push_target_max_size is None:
        return True
    maximum = getattr(action.push_target_max_size, "value", action.push_target_max_size)
    return bool(re.search(rf"\b{re.escape(str(maximum))}\s+or\s+smaller\b", actions, re.IGNORECASE))


def save_action_issues(action: Any, actions: str) -> list[str]:
    issues: list[str] = []
    if action.name.lower() not in actions:
        issues.append(f"save-action-name-missing:{action.id}")
    save = rf"{action.save_ability}\s+Saving Throw:\s*DC\s*{action.dc}\b"
    if not re.search(save, actions, re.IGNORECASE):
        issues.append(f"save-dc-mismatch:{action.id}")
    if action.damage_dice_count and not _dice_pattern(
        action.damage_dice_count,
        action.damage_dice_size,
        action.damage_bonus,
    ).search(actions):
        issues.append(f"save-damage-mismatch:{action.id}")
    if not _push_present(action, actions):
        issues.append(f"save-push-rider-mismatch:{action.id}")
    if action.grapple_escape_dc is not None:
        if "grappled" not in actions or f"escape dc {action.grapple_escape_dc}" not in actions:
            issues.append(f"save-grapple-rider-mismatch:{action.id}")
    issues.extend(area_save_issues(action, actions))
    issues.extend(failure_effect_issues(action, actions))
    return issues
