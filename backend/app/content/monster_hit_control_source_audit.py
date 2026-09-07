from __future__ import annotations

import re
from typing import Any

from app.domain.models import WeaponAttack


def _max_size_present(actions: str, size: Any, condition: str) -> bool:
    size_name = getattr(size, "value", size)
    return bool(re.search(rf"\b{re.escape(str(size_name))}\s+or\s+smaller\b", actions, re.I) and condition.lower() in actions.lower())


def _timing_present(actions: str, control: Any) -> bool:
    if control.condition_id is None: return True
    if not re.search(rf"\b{re.escape(control.condition_id)}\s+condition\b", actions, re.I): return False
    timing = control.expiry_timing or ("source_turn_start" if control.expires_at_start_of_source_turn else None)
    target = {"target_turn_start": "start", "target_turn_end": "end"}.get(timing)
    if target: return bool(re.search(rf"until\s+the\s+{target}\s+of\s+its\s+next\s+turn", actions, re.I))
    source = {"source_turn_start": "start", "source_turn_end": "end"}.get(timing)
    if source: return bool(re.search(rf"until\s+the\s+{source}\s+of\s+the\s+[^.]+?[’']s\s+next\s+turn", actions, re.I))
    return True


def _eligibility_clause(actions: str) -> str:
    match = re.search(r"If the target is a creature that[^.]+\.", actions, re.I)
    return match.group(0).lower() if match else ""


def hit_control_issues(attack: WeaponAttack, actions: str) -> list[str]:
    control = attack.control_effect
    if control is None: return []
    issues: list[str] = []
    if control.grapple_escape_dc is not None:
        if "grappled" not in actions.lower() or not re.search(rf"escape\s+DC\s*{control.grapple_escape_dc}\b", actions, re.I):
            issues.append(f"grapple-rider-mismatch:{attack.id}")
        if control.max_target_size is not None and not _max_size_present(actions, control.max_target_size, "grappled"):
            issues.append(f"grapple-size-mismatch:{attack.id}")
        if control.restrains_while_grappled and "restrained" not in actions.lower():
            issues.append(f"restrained-rider-mismatch:{attack.id}")
        if control.grapple_escape_check_disadvantage and not re.search(
            r"Ability checks made to escape this grapple have Disadvantage", actions, re.I,
        ):
            issues.append(f"grapple-escape-disadvantage-mismatch:{attack.id}")
    if control.condition_id is not None and not _timing_present(actions, control):
        issues.append(f"condition-rider-mismatch:{attack.id}:{control.condition_id}")
    if control.initial_save_ability is not None:
        save = rf"\b{re.escape(control.initial_save_ability)}\s+Saving Throw:\s*DC\s*{control.initial_save_dc}\b"
        if not re.search(save, actions, re.I): issues.append(f"hit-condition-save-mismatch:{attack.id}")
    clause = _eligibility_clause(actions)
    for creature_type in control.excluded_creature_types:
        if not re.search(rf"\b{re.escape(creature_type.lower())}\b", clause): issues.append(f"hit-condition-type-exclusion-mismatch:{attack.id}:{creature_type}")
    for species_id in control.excluded_species_ids:
        if not re.search(rf"\b{re.escape(species_id.lower())}\b", clause): issues.append(f"hit-condition-species-exclusion-mismatch:{attack.id}:{species_id}")
    return issues
