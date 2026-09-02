from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.content.subclass_combat_overlays import (
    subclass_combat_features,
    subclass_feature_ids_for_class,
    subclass_ignored_ids_for_class,
    subclass_overlay,
)


def _level_row(rows: Mapping[int, Any], level: int) -> Any:
    if level not in rows:
        raise ValueError(f"Combat class level {level} must be present in the 1-20 class spine.")
    return rows[level]


def _items(row: Any, field: str) -> tuple[str, ...]:
    return tuple(getattr(row, field, ()))


def base_class_combat_features(class_id: str, level: int, rows: Mapping[int, Any]) -> tuple[str, ...]:
    """Compile universal class/build features only; subclass features are layered afterward."""
    _level_row(rows, level)
    subclass_ids = subclass_feature_ids_for_class(class_id)
    active: list[str] = []
    for current in range(1, level + 1):
        row = _level_row(rows, current)
        removed = [feature for feature in _items(row, "features_removed") if feature not in subclass_ids]
        added = [feature for feature in _items(row, "features_added") if feature not in subclass_ids]
        active = [feature for feature in active if feature not in removed]
        active.extend(feature for feature in added if feature not in active)
    return tuple(active)


def compose_class_subclass_features(
    class_id: str,
    subclass_id: str,
    level: int,
    rows: Mapping[int, Any],
) -> tuple[str, ...]:
    """Always build the base class first, then apply the selected sparse subclass overlay."""
    overlay = subclass_overlay(subclass_id)
    if overlay.class_id != class_id:
        raise ValueError(f"Subclass {subclass_id} belongs to {overlay.class_id}, not {class_id}.")
    active = list(base_class_combat_features(class_id, level, rows))
    for feature in subclass_combat_features(subclass_id, level):
        if feature not in active:
            active.append(feature)
    return tuple(active)


def base_class_arena_ignored(class_id: str, level: int, rows: Mapping[int, Any]) -> tuple[str, ...]:
    _level_row(rows, level)
    subclass_ignored = subclass_ignored_ids_for_class(class_id)
    ignored: list[str] = []
    for current in range(1, level + 1):
        row = _level_row(rows, current)
        ignored.extend(
            feature for feature in _items(row, "arena_ignored")
            if feature not in subclass_ignored and feature not in ignored
        )
    return tuple(ignored)
