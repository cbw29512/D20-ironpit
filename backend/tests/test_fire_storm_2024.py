from __future__ import annotations

from app.combat.area_targeting import legal_area_placements, member_in_area_placement
from app.combat.landing_offense_policy import decide_post_move_offense
from app.combat.spell_policy import choose_spell
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=abs(x) * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _setup(caster: EncounterCombatant, *enemies: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[caster],
        monsters=list(enemies),
        hero_total_levels=caster.state.template.level,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )


def test_fire_storm_places_ten_face_adjacent_cubes_over_spread_enemies() -> None:
    caster = _member(build_thalen_greenbough_level(13), "thalen", "heroes", 1, 7)
    enemies = [
        _member(build_commoner(), f"enemy-{index}", "monsters", 4 + index * 2, 7)
        for index in range(5)
    ]
    setup = _setup(caster, *enemies)
    storm = next(item for item in caster.state.template.spell_save_actions if item.id == "fire-storm")

    placements = legal_area_placements(caster, setup, storm.area, storm.range_ft)
    assert placements
    best = placements[0]
    assert len(best.target_ids) == 5
    assert 2 <= len(best.cube_sw_cells) <= 10
    cells = set(best.cube_sw_cells)
    assert len(cells) == len(best.cube_sw_cells)
    span = 2
    for sx, sy in cells:
        neighbors = {(sx + span, sy), (sx - span, sy), (sx, sy + span), (sx, sy - span)}
        if len(cells) > 1:
            assert neighbors & cells
    assert all(member_in_area_placement(caster, enemy, storm.area, best) for enemy in enemies)


def test_landing_damage_selects_fire_storm_when_it_is_the_highest_landable_damage() -> None:
    caster = _member(build_seraphine_dawnshield_level(13), "seraphine", "heroes", 1, 7)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 80}, deep=True), "enemy", "monsters", 10, 7)
    setup = _setup(caster, enemy)
    begin_turn(caster.state)

    choice = choose_spell(caster, setup, "1:seraphine")
    assert choice is not None
    assert choice.action.id == "fire-storm"
    assert choice.placement is not None
    assert enemy.combatant_id in choice.placement.target_ids
    assert choice.placement.cube_sw_cells

    pick = decide_post_move_offense(caster, setup, "1:seraphine")
    assert pick.family == "spell"
    assert pick.expected_damage == choice.expected_damage
