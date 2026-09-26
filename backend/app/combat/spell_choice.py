from __future__ import annotations

from dataclasses import dataclass

from app.combat.spell_area import AreaPlacement
from app.domain.spells import SpellSaveAction


@dataclass(frozen=True)
class SpellChoice:
    action: SpellSaveAction
    slot_level: int
    target_ids: tuple[str, ...]
    placement: AreaPlacement | None = None
    expected_damage: float = 0.0
