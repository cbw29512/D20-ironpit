from app.combat.spell_area import area_slot_count, best_area_placement
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(side: str, index: int, position: int):
    template = build_karnok_stoneward() if side == "heroes" else build_goblin_warrior()
    return EncounterCombatant(
        combatant_id=f"{side}-{index}", side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(hero_count: int, monster_count: int, hero_position: int = 0, monster_position: int = 30):
    heroes = [_member("heroes", index, hero_position) for index in range(hero_count)]
    monsters = [_member("monsters", index, monster_position) for index in range(monster_count)]
    return EncounterSetup(
        heroes=heroes, monsters=monsters, hero_total_levels=hero_count,
        monster_total_cr=str(monster_count / 4), starting_distance_ft=monster_position - hero_position,
    )


def test_radius_maps_to_adjacent_card_slots() -> None:
    assert area_slot_count(5) == 1
    assert area_slot_count(10) == 2
    assert area_slot_count(20) == 4
    assert area_slot_count(30) == 6
    assert area_slot_count(60) == 6


def test_twenty_foot_area_can_cover_four_adjacent_enemies() -> None:
    setup = _setup(1, 6, monster_position=30)
    result = best_area_placement(setup.heroes[0], setup, 20, 150)
    assert result is not None
    assert len(result.enemy_ids) == 4
    assert result.friendly_ids == ()


def test_thirty_foot_area_can_cover_all_six_enemy_cards() -> None:
    setup = _setup(1, 6, monster_position=60)
    result = best_area_placement(setup.heroes[0], setup, 30, 150)
    assert result is not None
    assert len(result.enemy_ids) == 6


def test_aoe_is_cast_when_enemies_outnumber_friends() -> None:
    setup = _setup(1, 3, monster_position=5)
    result = best_area_placement(setup.heroes[0], setup, 20, 150)
    assert result is not None
    assert len(result.enemy_ids) == 3
    assert result.friendly_ids == ("heroes-0",)


def test_aoe_is_rejected_when_enemies_do_not_outnumber_friends() -> None:
    setup = _setup(2, 2, monster_position=5)
    assert best_area_placement(setup.heroes[0], setup, 10, 150) is None


def test_raw_feature_protection_removes_spared_friends_from_risk_count() -> None:
    setup = _setup(2, 2, monster_position=5)
    result = best_area_placement(
        setup.heroes[0], setup, 10, 150,
        protected_ally_ids={"heroes-0", "heroes-1"},
    )
    assert result is not None
    assert len(result.enemy_ids) == 2
    assert result.friendly_ids == ()
    assert result.protected_friendly_ids == ("heroes-0", "heroes-1")


def test_area_does_not_jump_over_an_occupied_card_space() -> None:
    setup = _setup(1, 3, monster_position=30)
    setup.monsters[1].state.current_hp = 0
    setup.monsters[1].state.is_alive = False
    setup.monsters[1].state.is_dead = True
    result = best_area_placement(setup.heroes[0], setup, 10, 150)
    assert result is not None
    assert len(result.enemy_ids) == 1
