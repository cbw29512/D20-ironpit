from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def _action_prefix(action: Any) -> str:
    name = re.escape(str(action.name))
    recharge = r"(?:\s+\(Recharge\s+\d(?:\s*[-–]\s*\d)?\))?"
    return rf"\b{name}{recharge}\."


def _save_header(action: Any) -> str:
    ability = re.escape(str(action.save_ability))
    return rf"{ability}\s+Saving Throw:\s*DC\s*{action.dc}\b"


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
        return rf"each creature in a {area.radius_ft}-foot-radius Sphere centered on (?:that|a) point\b"
    raise ValueError(f"Unsupported source-audit area shape: {area.shape!r}.")


def _point_range_present(action: Any, action_text: str) -> bool:
    area = action.area
    if area is None or area.shape != "radius":
        return True
    pattern = rf"\bpoint\b.{{0,100}}?\bwithin\s+{action.range_ft}\s+feet\b"
    return bool(re.search(pattern, action_text, re.IGNORECASE))


def area_save_issues(action: Any, actions: str) -> list[str]:
    """Verify one source action's geometry and save-damage semantics without depending on prose order."""
    try:
        targeting = _targeting_pattern(action)
        if targeting is None:
            return []
        prefix = _action_prefix(action)
        match = re.search(prefix + r"(?P<body>.{0,900}?)(?=\b[A-Z][A-Za-z’' -]+(?:\s+\([^)]*\))?\.\s|$)", actions, re.IGNORECASE)
        action_text = match.group(0) if match else ""
        save = _save_header(action)
        issues: list[str] = []
        if not action_text or not re.search(save, action_text, re.IGNORECASE):
            return [
                f"save-area-mismatch:{action.id}",
                *([f"save-damage-type-mismatch:{action.id}"] if action.damage_type is not None else []),
                *([f"save-success-damage-mismatch:{action.id}"] if action.success_damage == "half" else []),
            ]
        if not _point_range_present(action, action_text) or not re.search(targeting, action_text, re.IGNORECASE):
            issues.append(f"save-area-mismatch:{action.id}")
        if action.damage_type is not None:
            damage_type = re.escape(str(action.damage_type))
            if not re.search(rf"\b{damage_type}\s+damage\b", action_text, re.IGNORECASE):
                issues.append(f"save-damage-type-mismatch:{action.id}")
        if action.success_damage == "half":
            if not re.search(r"\bSuccess:\s*Half damage(?:\s+only)?\b", action_text, re.IGNORECASE):
                issues.append(f"save-success-damage-mismatch:{action.id}")
        return issues
    except Exception:
        logger.exception("Failed area save source audit for %s.", action.id)
        raise
