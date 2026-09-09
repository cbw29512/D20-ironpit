from __future__ import annotations

import re

from app.combat.grid_geometry import footprints_overlap, position_in_bounds
from app.combat.grid_placement import apply_placement, pack_deployment_zone
from app.combat.state import build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.demo import build_goblin_warrior
from app.content.monster_catalog import load_monster_rows
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant
from app.domain.grid import DeploymentZone
from app.domain.size import CreatureSize


def _member(combatant_id: str, size: CreatureSize) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(
        update={"id": combatant_id, "name": combatant_id, "size": size},
    )
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )


def test_standard_vtt_map_is_24_by_16_five_foot_squares() -> None:
    battle_map = build_standard_iron_pit_map()

    assert battle_map.width_squares == 24
    assert battle_map.height_squares == 16
    assert battle_map.cell_size_ft == 5


def test_six_gargantuan_combatants_fit_in_an_eight_by_twelve_deployment_zone() -> None:
    battle_map = build_standard_iron_pit_map()
    zone = DeploymentZone(x=0, y=2, width_squares=8, height_squares=12, front_edge="east")
    members = [_member(f"gargantuan-{index}", CreatureSize.GARGANTUAN) for index in range(6)]

    assignments = pack_deployment_zone(battle_map, zone, members)
    apply_placement(members, assignments)

    assert all(member.state.position is not None for member in members)
    for member in members:
        assert position_in_bounds(battle_map, member.state.position, member.state.template.size)
    for index, member in enumerate(members):
        for other in members[index + 1:]:
            assert not footprints_overlap(
                member.state.position,
                member.state.template.size,
                other.state.position,
                other.state.template.size,
            )


def test_all_330_canonical_monster_rows_have_supported_printed_sizes() -> None:
    rows = load_monster_rows()
    supported = {size.value for size in CreatureSize}

    assert len(rows) == 330
    for row in rows:
        source_size = str(row["size"]).strip().lower()
        allowed = {size for size in supported if re.search(rf"\b{re.escape(size)}\b", source_size)}
        assert allowed, f"Unsupported SRD size wording for {row['name']}: {row['size']!r}"


def test_every_runtime_monster_size_matches_its_canonical_srd_row() -> None:
    source_by_name = {str(row["name"]): str(row["size"]).strip().lower() for row in load_monster_rows()}
    supported = {size.value for size in CreatureSize}
    monsters = build_arena_roster().monsters

    assert monsters
    for monster in monsters:
        assert monster.name in source_by_name
        source_size = source_by_name[monster.name]
        allowed = {size for size in supported if re.search(rf"\b{re.escape(size)}\b", source_size)}
        assert monster.size.value in allowed
