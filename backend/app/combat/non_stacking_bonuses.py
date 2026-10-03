from __future__ import annotations

from collections.abc import Iterable

from app.domain.modifiers import CombatModifier


def non_stacking_flat_total(modifiers: Iterable[CombatModifier]) -> int:
    """Sum ordinary bonuses while taking the strongest value in each declared group."""
    ungrouped = 0
    grouped: dict[str, int] = {}
    for item in modifiers:
        if item.non_stacking_group is None:
            ungrouped += item.flat_bonus
        else:
            grouped[item.non_stacking_group] = max(
                grouped.get(item.non_stacking_group, 0),
                item.flat_bonus,
            )
    return ungrouped + sum(grouped.values())
