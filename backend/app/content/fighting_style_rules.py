from __future__ import annotations

from collections.abc import Iterable

FightingStyleSelection = str | Iterable[str] | None


def has_fighting_style(selection: FightingStyleSelection, style: str) -> bool:
    if selection is None:
        return False
    if isinstance(selection, str):
        return selection == style
    return style in selection
