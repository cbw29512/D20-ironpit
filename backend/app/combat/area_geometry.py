from __future__ import annotations

from app.domain.encounters import EncounterCombatant

MAX_CARD_SLOTS = 6
CARD_WIDTH_FT = 5


def area_slot_count(radius_ft: int) -> int:
    """Compact-card abstraction for lateral coverage; depth uses point placement."""
    if radius_ft < CARD_WIDTH_FT or radius_ft % CARD_WIDTH_FT:
        raise ValueError("Iron Pit spell radii must be positive 5-foot increments.")
    return min(MAX_CARD_SLOTS, radius_ft // CARD_WIDTH_FT)


def area_contains(
    member: EncounterCombatant,
    slot_index: int,
    start_slot: int,
    slot_count: int,
    center_ft: int,
    radius_ft: int,
) -> bool:
    return (
        start_slot <= slot_index < start_slot + slot_count
        and abs(member.position_ft - center_ft) <= radius_ft
    )


def candidate_area_centers(
    caster: EncounterCombatant,
    members: list[EncounterCombatant],
    radius_ft: int,
    spell_range_ft: int,
) -> list[int]:
    """Search legal 5-foot points, including edge placements beyond occupied positions."""
    if not members:
        return []
    minimum = min(member.position_ft for member in members) - radius_ft
    maximum = max(member.position_ft for member in members) + radius_ft
    return [
        point
        for point in range(minimum, maximum + CARD_WIDTH_FT, CARD_WIDTH_FT)
        if abs(caster.position_ft - point) <= spell_range_ft
    ]
