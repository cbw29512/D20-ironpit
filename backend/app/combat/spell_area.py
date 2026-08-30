from __future__ import annotations

from dataclasses import dataclass

from app.domain.encounters import EncounterCombatant, EncounterSetup

MAX_CARD_SLOTS = 6
CARD_WIDTH_FT = 5


@dataclass(frozen=True)
class AreaPlacement:
    start_slot: int
    slot_count: int
    center_ft: int
    enemy_ids: tuple[str, ...]
    friendly_ids: tuple[str, ...]
    protected_friendly_ids: tuple[str, ...]

    @property
    def worthwhile(self) -> bool:
        return len(self.enemy_ids) > len(self.friendly_ids)


def area_slot_count(radius_ft: int) -> int:
    """Iron Pit abstraction: every 5 feet of radius covers one adjacent card slot."""
    if radius_ft < CARD_WIDTH_FT or radius_ft % CARD_WIDTH_FT:
        raise ValueError("Iron Pit spell radii must be positive 5-foot increments.")
    return min(MAX_CARD_SLOTS, radius_ft // CARD_WIDTH_FT)


def _living(member: EncounterCombatant) -> bool:
    state = member.state
    return state.is_alive and not state.is_dead and state.current_hp > 0


def _side_rows(caster: EncounterCombatant, setup: EncounterSetup):
    if caster.side == "heroes":
        return setup.monsters, setup.heroes
    return setup.heroes, setup.monsters


def _inside(
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


def best_area_placement(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    radius_ft: int,
    spell_range_ft: int,
    protected_ally_ids: set[str] | None = None,
) -> AreaPlacement | None:
    """Choose the best contiguous area; reject it unless enemies outnumber exposed friends."""
    slot_count = area_slot_count(radius_ft)
    enemies, friends = _side_rows(caster, setup)
    protected = protected_ally_ids or set()
    living_enemies = [member for member in enemies if _living(member)]
    if not living_enemies:
        return None

    candidates: list[AreaPlacement] = []
    for anchor in living_enemies:
        center_ft = anchor.position_ft
        if abs(caster.position_ft - center_ft) > spell_range_ft:
            continue
        for start in range(0, MAX_CARD_SLOTS - slot_count + 1):
            enemy_ids = tuple(
                member.combatant_id for index, member in enumerate(enemies)
                if _living(member) and _inside(member, index, start, slot_count, center_ft, radius_ft)
            )
            if not enemy_ids:
                continue
            exposed, spared = [], []
            for index, member in enumerate(friends):
                if not _living(member) or not _inside(member, index, start, slot_count, center_ft, radius_ft):
                    continue
                (spared if member.combatant_id in protected else exposed).append(member.combatant_id)
            placement = AreaPlacement(start, slot_count, center_ft, enemy_ids, tuple(exposed), tuple(spared))
            if placement.worthwhile:
                candidates.append(placement)

    if not candidates:
        return None
    return max(
        candidates,
        key=lambda item: (
            len(item.enemy_ids) - len(item.friendly_ids),
            len(item.enemy_ids),
            -len(item.friendly_ids),
            -item.start_slot,
        ),
    )
