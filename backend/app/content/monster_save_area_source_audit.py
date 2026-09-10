from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def _header(action: Any) -> str:
    name = re.escape(str(action.name))
    recharge = r"(?:\s+\(Recharge\s+\d(?:\s*[-–]\s*\d)?\))?"
    save = rf"{re.escape(str(action.save_ability))}\s+Saving Throw:\s*DC\s*{action.dc}\b"
    return rf"\b{name}{recharge}\..{{0,300}}?{save}"


def _targeting_pattern(action: Any) -> str | None:
    area = action.area
    if area is None:
        return None
    if area.shape == "cone":
        if action.range_ft != 0:
            return r"(?!)"
        return rf"each creature in a {area.length_ft}-foot Cone\b"
    if area.shape == "line":
        if action.range_ft != 0:
            return r"(?!)"
        return rf"each creature in a {area.length_ft}-foot-long,\s*{area.width_ft}-foot-wide Line\b"
    if area.shape == "emanation":
        if action.range_ft != 0:
            return r"(?!)"
        return rf"each creature in a {area.radius_ft}-foot Emanation originating from\b"
    if area.shape == "radius":
        return (
            rf"each creature in a {area.radius_ft}-foot-radius Sphere centered on "
            rf"(?:that point|a point(?: within {action.range_ft} feet)?)\b"
        )
    raise ValueError(f"Unsupported source-audit area shape: {area.shape!r}.")


def _point_range_present(action: Any, actions: str) -> bool:
    area = action.area
    if area is None or area.shape != "radius":
        return True
    prefix = _header(action)
    before_save = (
        rf"\b{re.escape(str(action.name))}(?:\s+\(Recharge\s+\d(?:\s*[-–]\s*\d)?\))?\."
        rf".{{0,250}}?\bpoint\b.{{0,100}}?\bwithin\s+{action.range_ft}\s+feet\b"
    )
    target_range = rf"centered on a point within {action.range_ft} feet\b"
    return bool(re.search(before_save, actions, re.IGNORECASE) or re.search(prefix + rf".{{0,700}}?{target_range}", actions, re.IGNORECASE))


def area_save_issues(action: Any, actions: str) -> list[str]:
    """Verify source geometry and save-damage semantics for an area Saving Throw action."""
    try:
        targeting = _targeting_pattern(action)
        if targeting is None:
            return []
        header = _header(action)
        clause = rf"{header}.{{0,700}}?"
        issues: list[str] = []
        if not _point_range_present(action, actions) or not re.search(clause + targeting, actions, re.IGNORECASE):
            issues.append(f"save-area-mismatch:{action.id}")
        if action.damage_type is not None:
            damage_type = re.escape(str(action.damage_type))
            if not re.search(clause + rf"\b{damage_type}\s+damage\b", actions, re.IGNORECASE):
                issues.append(f"save-damage-type-mismatch:{action.id}")
        if action.success_damage == "half":
            if not re.search(clause + r"\bSuccess:\s*Half damage(?:\s+only)?\b", actions, re.IGNORECASE):
                issues.append(f"save-success-damage-mismatch:{action.id}")
        return issues
    except Exception:
        logger.exception("Failed area save source audit for %s.", action.id)
        raise
