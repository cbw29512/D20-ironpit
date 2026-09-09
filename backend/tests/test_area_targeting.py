from __future__ import annotations

from app.combat.area_targeting import legal_area_placements
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.size import CreatureSize
from app.domain.targeting import AreaTargeting


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_karnok_stoneward() if side == "heroes" else build_goblin_warrior()
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _setup(heroes: list[EncounterCombatant], monsters: list[EncounterCombatant]) -> EncounterSetup:
    return EncounterSetup(
        heroes=heroes,
        monsters=monsters,
        hero_total_levels=max(1, len(heroes)),
        monster_total_cr="1",
        map_definition=BattleMapDefinition(id="area-test", width_squares=24, height_squares=16),
    )


def test_offensive_area_targeting_is_always_ally_safe() -> None:
    actor = _member("actor", "heroes", 1, 5)
    ally = _member("ally", "heroes", 2, 5)
    first = _member("first", "monsters", 2, 5)
    second = _member("second", "monsters", 3, 5)
    area = AreaTargeting(shape="cone", origin="self", length_ft=15)
    placements = legal_area_placements(actor, _setup([actor, ally], [first, second]), area, 0)
    assert placements
    assert placements[0].target_ids == ("first", "second")
    assert all("ally" not in placement.target_ids for placement in placements)


def test_dead_enemies_are_not_area_targets() -> None:
    actor = _member("actor", "heroes", 1, 5)
    living = _member("living", "monsters", 2, 5)
    dead = _member("dead", "monsters", 3, 5)
    dead.state.current_hp = 0
    dead.state.is_alive = False
    dead.state.is_dead = True
    area = AreaTargeting(shape="line", origin="self", length_ft=30, width_ft=5)
    placements = legal_area_placements(actor, _setup([actor], [living, dead]), area, 0)
    assert placements
    assert all("dead" not in placement.target_ids for placement in placements)


def test_large_footprint_is_hit_when_any_occupied_square_is_covered() -> None:
    actor = _member("actor", "heroes", 0, 0)
    target = _member("large", "monsters", 4, 0)
    target.state.template = target.state.template.model_copy(update={"size": CreatureSize.LARGE})
    area = AreaTargeting(shape="radius", origin="point", radius_ft=5)
    placements = legal_area_placements(actor, _setup([actor], [target]), area, 60)
    assert any(placement.origin == (32.5, 2.5) and placement.target_ids == ("large",) for placement in placements)


def test_missing_grid_position_fails_closed_instead_of_using_scalar_distance() -> None:
    actor = _member("actor", "heroes", 0, 0)
    target = _member("target", "monsters", 2, 0)
    target.state.position = None
    area = AreaTargeting(shape="cone", origin="self", length_ft=15)
    try:
        legal_area_placements(actor, _setup([actor], [target]), area, 0)
    except ValueError as exc:
        assert "authoritative grid position" in str(exc)
    else:
        raise AssertionError("Area targeting silently fell back from the authoritative grid.")
