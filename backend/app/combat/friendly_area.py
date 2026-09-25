from __future__ import annotations

from dataclasses import dataclass

from app.combat.area_geometry import (
    MAX_CARD_SLOTS,
    area_contains,
    area_slot_count,
    candidate_area_centers,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup


@dataclass(frozen=True)
class FriendlyAreaPlacement:
    start_slot: int
    slot_count: int
    center_ft: int
    target_ids: tuple[str, ...]


def _friendly_row(caster: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    return setup.heroes if caster.side == "heroes" else setup.monsters


def best_friendly_area_placement(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    radius_ft: int,
    spell_range_ft: int,
    eligible_ids: set[str],
    required_ids: set[str] | None = None,
) -> FriendlyAreaPlacement | None:
    """Maximize eligible friendly targets inside one legal source-defined area."""
    slot_count = area_slot_count(radius_ft)
    friends = _friendly_row(caster, setup)
    eligible = [member for member in friends if member.combatant_id in eligible_ids]
    if not eligible:
        return None
    required = required_ids or set()
    candidates: list[FriendlyAreaPlacement] = []
    for center_ft in candidate_area_centers(caster, eligible, radius_ft, spell_range_ft):
        for start in range(0, MAX_CARD_SLOTS - slot_count + 1):
            target_ids = tuple(
                member.combatant_id
                for index, member in enumerate(friends)
                if member.combatant_id in eligible_ids
                and area_contains(member, index, start, slot_count, center_ft, radius_ft)
            )
            if not target_ids or not required.issubset(target_ids):
                continue
            candidates.append(FriendlyAreaPlacement(start, slot_count, center_ft, target_ids))
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda item: (
            len(item.target_ids),
            -abs(caster.position_ft - item.center_ft),
            -item.start_slot,
        ),
    )
