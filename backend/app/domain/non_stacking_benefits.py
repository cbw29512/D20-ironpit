from __future__ import annotations


def normalize_non_stacking_group(kind: object, flat_bonus: int, group: str | None) -> str | None:
    """Validate and normalize a declared non-stacking flat-benefit group."""
    if group is None:
        return None
    kind_value = getattr(kind, "value", str(kind))
    if kind_value not in {"armor-class", "saving-throw-flat"}:
        raise ValueError("Non-stacking groups support AC and saving-throw flat benefits only.")
    if flat_bonus <= 0:
        raise ValueError("Non-stacking grouped benefits require a positive flat bonus.")
    return group.strip().casefold()
