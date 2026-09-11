from __future__ import annotations

import re

from app.domain.models import WeaponAttack


def on_hit_save_issues(attack: WeaponAttack, actions: str) -> list[str]:
    rider = attack.on_hit_saving_throw
    if rider is None:
        return []
    issues: list[str] = []
    save_pattern = rf"\b{rider.save_ability}\s+Saving Throw:\s*DC\s*{rider.dc}\b"
    if not re.search(save_pattern, actions, re.I):
        issues.append(f"on-hit-save-mismatch:{attack.id}")
    for effect in rider.failure_effects:
        if effect.kind != "condition":
            continue
        condition = getattr(effect, "condition", None)
        if condition and not re.search(rf"Failure:\s*(?:The\s+)?target has the {condition} condition\b", actions, re.I):
            issues.append(f"on-hit-save-condition-mismatch:{attack.id}:{condition}")
        timing = getattr(effect, "expiry_timing", None)
        edge = {
            "target_turn_start": r"until the start of its next turn",
            "target_turn_end": r"until the end of its next turn",
            "source_turn_start": r"until the start of the [^.]+?[’']s next turn",
            "source_turn_end": r"until the end of the [^.]+?[’']s next turn",
        }.get(timing)
        if edge and not re.search(edge, actions, re.I):
            issues.append(f"on-hit-save-timing-mismatch:{attack.id}:{timing}")
    return issues


__all__ = ["on_hit_save_issues"]