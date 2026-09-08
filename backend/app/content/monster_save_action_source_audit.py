from __future__ import annotations

import re
from typing import Any, Callable


def save_action_issues(
    action: Any,
    actions: str,
    dice_pattern: Callable[[int, int, int], re.Pattern[str]],
) -> list[str]:
    issues: list[str] = []
    if action.name.lower() not in actions:
        issues.append(f"save-action-name-missing:{action.id}")
    save = rf"{action.save_ability}\s+Saving Throw:\s*DC\s*{action.dc}\b"
    if not re.search(save, actions, re.IGNORECASE):
        issues.append(f"save-dc-mismatch:{action.id}")
    if action.damage_dice_count and not dice_pattern(
        action.damage_dice_count, action.damage_dice_size, action.damage_bonus,
    ).search(actions):
        issues.append(f"save-damage-mismatch:{action.id}")
    control = action.failure_control
    if control is None and action.grapple_escape_dc is not None:
        escape_dc = action.grapple_escape_dc
        restrains = action.restrains_while_grappled
        max_size = action.target_max_size
    elif control is not None:
        escape_dc = control.grapple_escape_dc
        restrains = control.restrains_while_grappled
        max_size = control.max_target_size
    else:
        escape_dc = None; restrains = False; max_size = None
    if escape_dc is not None:
        if "grappled" not in actions.lower() or not re.search(rf"escape\s+DC\s+{escape_dc}\b", actions, re.I):
            issues.append(f"save-grapple-rider-mismatch:{action.id}")
        if max_size is not None:
            size = getattr(max_size, "value", max_size)
            if not re.search(rf"\b{re.escape(str(size))}\s+or\s+smaller\b", actions, re.I):
                issues.append(f"save-grapple-size-mismatch:{action.id}")
        if restrains and "restrained" not in actions.lower():
            issues.append(f"save-restrained-rider-mismatch:{action.id}")
    if control is not None and control.condition_id is not None:
        if not re.search(rf"\b{re.escape(control.condition_id)}\s+condition\b", actions, re.I):
            issues.append(f"save-condition-rider-mismatch:{action.id}:{control.condition_id}")
    return issues
