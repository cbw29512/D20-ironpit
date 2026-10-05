from __future__ import annotations

from app.combat.grid_pathing_support import movement_step_cost_ft
from app.combat.spell_policy import choose_spell, spell_at_slot
from app.combat.spell_resolution import resolve_spell
from app.combat.state import begin_turn, build_combatant_state
from app.combat.dice import FixedDiceProvider
from app.combat.temporary_terrain import destination_is_difficult_terrain, expire_source_terrain
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.monsters import build_commoner
from app.content.storm_spell_effects import build_ice_storm_2024
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


def _ice_druid() -> EncounterCombatant:
    template = build_thalen_greenbough_level(20).model_copy(update={
        "spell_save_actions": [build_ice_storm_2024(17)],
        "spell_attack_actions": [],
    })
    return _member(template, "thalen", "heroes", 2, 7)


def test_ice_storm_prints_mixed_damage_and_temporary_difficult_terrain() -> None:
    spell = build_ice_storm_2024(17)
    assert spell.id == "ice-storm"
    assert spell.level == 4
    assert spell.range_ft == 300
    assert spell.area is not None
    assert (spell.area.shape, spell.area.radius_ft) == ("radius", 20)
    assert spell.creates_difficult_terrain is True
    assert spell.difficult_terrain_duration_rounds == 1
    assert [
        (part.dice_count, part.dice_size, part.damage_type, part.upcast_dice_per_level)
        for part in spell.damage_components
    ] == [(2, 10, "bludgeoning", 1), (4, 8, "cold", 0)]
    scaled = spell_at_slot(spell, 5)
    assert [
        (part.dice_count, part.dice_size, part.damage_type)
        for part in scaled.damage_components
    ] == [(3, 10, "bludgeoning"), (4, 8, "cold")]


def test_ice_storm_places_magical_difficult_terrain_until_end_of_next_turn() -> None:
    caster = _ice_druid()
    caster.state.resources = [
        item for item in caster.state.resources if item.id == "spell-slot-4"
    ]
    enemy = _member(build_commoner().model_copy(update={"max_hp": 80}, deep=True), "enemy", "monsters", 6, 7)
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[enemy],
        hero_total_levels=20,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )
    begin_turn(caster.state)
    choice = choose_spell(caster, setup, "1:thalen")
    assert choice is not None
    assert choice.action.id == "ice-storm"
    assert choice.placement is not None

    resolve_spell(
        1, 1, caster, setup, choice, "1:thalen",
        FixedDiceProvider([1, 10, 10, 8, 8, 8, 8]),
    )
    assert setup.temporary_terrain_zones
    zone = setup.temporary_terrain_zones[0]
    assert zone.action_id == "ice-storm"
    assert zone.radius_ft == 20
    assert zone.source_is_magical is True
    assert zone.expires_round == 2
    assert zone.expiry_timing == "source_turn_end"

    assert destination_is_difficult_terrain(setup.temporary_terrain_zones, enemy, enemy.state.position)
    assert destination_is_difficult_terrain(setup.temporary_terrain_zones, enemy, zone.center)
    occupied = {
        (member.state.position.x, member.state.position.y)
        for member in (*setup.heroes, *setup.monsters)
        if member.state.position is not None
    }
    probe = next(
        GridPosition(x=zone.center.x + dx, y=zone.center.y + dy)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
        if 0 <= zone.center.x + dx < setup.map_definition.width_squares
        and 0 <= zone.center.y + dy < setup.map_definition.height_squares
        and (zone.center.x + dx, zone.center.y + dy) not in occupied
    )
    assert destination_is_difficult_terrain(setup.temporary_terrain_zones, enemy, probe)
    origin = GridPosition(
        x=probe.x + (1 if probe.x + 1 < setup.map_definition.width_squares else -1),
        y=probe.y,
    )
    step = movement_step_cost_ft(
        setup.map_definition,
        enemy,
        probe,
        [*setup.heroes, *setup.monsters],
        origin=origin,
        terrain_zones=setup.temporary_terrain_zones,
    )
    assert step == 10

    assert expire_source_terrain(setup, caster.combatant_id, 1) == []
    assert setup.temporary_terrain_zones
    assert expire_source_terrain(setup, caster.combatant_id, 2) == [zone.zone_id]
    assert setup.temporary_terrain_zones == []


def test_cube_difficult_terrain_without_radius_fails_closed() -> None:
    from app.combat.temporary_terrain import spell_terrain_is_supported
    from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
    from app.content.monster_source_2014 import load_monster_source_2014

    unicorn = next(item for item in load_monster_source_2014() if item.id == "unicorn")
    entangle = next(item for item in innate_spell_save_actions_2014(unicorn) if item.id == "entangle")
    assert spell_terrain_is_supported(build_ice_storm_2024(17)) is True
    assert spell_terrain_is_supported(entangle) is False
