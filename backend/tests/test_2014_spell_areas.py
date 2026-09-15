from app.combat.area_targeting import legal_area_placements
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monster_spell_actions_2014 import _save_spell
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(deep=True)
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
    )


def test_cone_of_cold_uses_universal_60_foot_cone() -> None:
    spell = _save_spell("cone-of-cold", 5, 17, 10)

    assert spell.save_ability == "constitution"
    assert spell.damage_dice_count == 8
    assert spell.damage_dice_size == 8
    assert spell.damage_type == "cold"
    assert spell.success_damage == "half"
    assert spell.area is not None
    assert spell.area.shape == "cone"
    assert spell.area.origin == "self"
    assert spell.area.length_ft == 60


def test_lightning_bolt_uses_universal_100_by_5_foot_line() -> None:
    spell = _save_spell("lightning-bolt", 3, 15, 7)

    assert spell.save_ability == "dexterity"
    assert spell.damage_dice_count == 8
    assert spell.damage_dice_size == 6
    assert spell.damage_type == "lightning"
    assert spell.success_damage == "half"
    assert spell.area is not None
    assert spell.area.shape == "line"
    assert spell.area.origin == "self"
    assert spell.area.length_ft == 100
    assert spell.area.width_ft == 5


def test_thunderwave_uses_universal_15_foot_cube_and_push() -> None:
    spell = _save_spell("thunderwave", 1, 13, 5)

    assert spell.save_ability == "constitution"
    assert spell.damage_dice_count == 2
    assert spell.damage_dice_size == 8
    assert spell.damage_type == "thunder"
    assert spell.success_damage == "half"
    assert spell.failure_push_ft == 10
    assert spell.area is not None
    assert spell.area.shape == "cube"
    assert spell.area.origin == "self"
    assert spell.area.length_ft == 15


def test_universal_spell_line_reports_friendly_fire_exposure() -> None:
    caster = _member("monster-1:caster", "monsters", 1, 1)
    ally = _member("monster-2:ally", "monsters", 2, 1)
    enemy = _member("hero-1:enemy", "heroes", 3, 1)
    setup = EncounterSetup(
        heroes=[enemy], monsters=[caster, ally], hero_total_levels=1,
        monster_total_cr="1/2",
        map_definition=BattleMapDefinition(id="spell-area", width_squares=12, height_squares=8),
    )
    spell = _save_spell("lightning-bolt", 3, 15, 7)

    placements = legal_area_placements(caster, setup, spell.area, spell.range_ft)
    exposed = next(item for item in placements if enemy.combatant_id in item.enemy_ids and ally.combatant_id in item.friendly_ids)

    assert exposed.enemy_ids == (enemy.combatant_id,)
    assert exposed.friendly_ids == (ally.combatant_id,)


def test_universal_spell_cube_can_cover_adjacent_targets() -> None:
    caster = _member("hero-1:caster", "heroes", 1, 1)
    first = _member("monster-1:first", "monsters", 2, 1)
    second = _member("monster-2:second", "monsters", 2, 2)
    setup = EncounterSetup(
        heroes=[caster], monsters=[first, second], hero_total_levels=1,
        monster_total_cr="1/2",
        map_definition=BattleMapDefinition(id="spell-cube", width_squares=8, height_squares=8),
    )
    spell = _save_spell("thunderwave", 1, 13, 5)

    placements = legal_area_placements(caster, setup, spell.area, spell.range_ft)

    assert any(set(item.enemy_ids) == {first.combatant_id, second.combatant_id} for item in placements)
