from __future__ import annotations

import re

from app.domain.swallow import SwallowAction


def swallow_action_issues(action: SwallowAction, actions: str) -> list[str]:
    """Verify declarative Swallow semantics against the SRD action text."""
    try:
        issues: list[str] = []
        size = action.max_target_size.value
        if not re.search(rf"\bSwallow\.\s+[^.]*\b{size}\s+or\s+smaller\b", actions, re.I):
            issues.append(f"swallow-target-size-mismatch:{action.id}")
        damage = rf"{action.damage_dice_count}\s*d\s*{action.damage_dice_size}"
        if not re.search(rf"{damage}[^.]*{action.damage_type.value}\s+damage", actions, re.I):
            issues.append(f"swallow-damage-mismatch:{action.id}")
        if action.applies_blinded and "blinded" not in actions.lower():
            issues.append(f"swallow-blinded-missing:{action.id}")
        if action.applies_restrained and "restrained" not in actions.lower():
            issues.append(f"swallow-restrained-missing:{action.id}")
        if action.total_cover_from_outside and "total cover" not in actions.lower():
            issues.append(f"swallow-total-cover-missing:{action.id}")
        if action.forbidden_attack_ids_while_active and not re.search(r"can(?:not|'t|’t)\s+use\s+Bite", actions, re.I):
            issues.append(f"swallow-attack-lockout-missing:{action.id}")
        if action.disgorge_after_first_tick and "disgorg" not in actions.lower():
            issues.append(f"swallow-disgorge-missing:{action.id}")
        if action.first_tick_delay_rounds == 1 and not re.search(r"end\s+of\s+the\s+[^.]+?next\s+turn", actions, re.I):
            issues.append(f"swallow-delay-mismatch:{action.id}")
        if action.first_tick_delay_rounds == 0 and not re.search(r"end\s+of\s+(?:each|the)\s+[^.]+?turn", actions, re.I):
            issues.append(f"swallow-timing-mismatch:{action.id}")
        if not re.search(r"only\s+one\s+target\s+swallowed\s+at\s+a\s+time|swallows\s+a\s+[^.]+?target\s+it\s+is\s+grappling", actions, re.I):
            issues.append(f"swallow-target-mode-mismatch:{action.id}")
        return issues
    except Exception as exc:
        raise RuntimeError(f"Swallow source audit failed for {action.id}.") from exc
