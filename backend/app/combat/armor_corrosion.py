"""Generic, fight-only armor-item AC corrosion; does not mutate a card.

Call only from a source-proven on-hit armor rider with verified equipment data.
The AC display and unarmored fallback remain separate runtime integrations.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.runtime import CombatantState


@dataclass(frozen=True)
class ArmorCorrosionResult:
    penalty: int
    destroyed: bool
    applied: bool


def corrode_armor_on_hit(
    state: CombatantState, armor_id: str, *,
    hit: bool, nonmagical_metal_armor: bool, item_base_ac: int,
    destroy_at_item_ac: int = 10,
) -> ArmorCorrosionResult:
    """Corrode a specific equipped armor item, never the target's total AC."""
    if not isinstance(armor_id, str) or not armor_id.strip():
        raise ValueError("Armor corrosion requires a stable item ID.")
    if not isinstance(hit, bool) or not isinstance(nonmagical_metal_armor, bool):
        raise ValueError("Armor corrosion requires verified hit and gear flags.")
    if (not isinstance(item_base_ac, int) or isinstance(item_base_ac, bool)
            or not isinstance(destroy_at_item_ac, int)
            or item_base_ac <= destroy_at_item_ac or destroy_at_item_ac < 0):
        raise ValueError("Armor corrosion requires verified item AC and floor.")
    current = state.armor_corrosion_penalties.get(armor_id, 0)
    if not 0 <= current <= item_base_ac - destroy_at_item_ac:
        raise ValueError("Invalid armor corrosion item state.")
    destroyed = armor_id in state.destroyed_armor_ids
    if not hit or not nonmagical_metal_armor or destroyed:
        return ArmorCorrosionResult(-current, destroyed, False)
    next_stacks = current + 1
    destroyed = item_base_ac - next_stacks <= destroy_at_item_ac
    state.armor_corrosion_penalties[armor_id] = next_stacks
    if destroyed:
        state.destroyed_armor_ids.append(armor_id)
    return ArmorCorrosionResult(-next_stacks, destroyed, True)
