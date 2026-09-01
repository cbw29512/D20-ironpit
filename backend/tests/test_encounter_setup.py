import pytest
from pydantic import ValidationError

from app.combat.encounter_setup import build_encounter_setup
from app.combat.formation import backline_holds_position, starting_position_ft
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.pregens import build_selene_asharrow
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import EncounterSelection


def test_builds_full_party_from_canonical_cards() -> None:
    encounter = build_encounter_setup(EncounterSelection(
        hero_ids=[
            "karnok-stoneward-l1", "rokhan-stonefury-l1",
            "karnok-stoneward-l1", "rokhan-stonefury-l1",
        ],
        monster_ids=["srd-goblin-warrior", "srd-goblin-warrior", "srd-guard"],
    ))
    assert len(encounter.heroes) == 4
    assert len(encounter.monsters) == 3
    assert encounter.hero_total_levels == 4
    assert encounter.monster_total_cr == "5/8"
    assert [hero.position_ft for hero in encounter.heroes] == [5, 5, 5, 5]
    assert [monster.position_ft for monster in encounter.monsters] == [10, 10, 10]
    assert "starting_distance_ft" not in encounter.model_dump()
    assert encounter.monsters[0].state.template.id == "srd-goblin-warrior"
    assert encounter.monsters[1].state.template.id == "srd-goblin-warrior"
    assert encounter.monsters[0].combatant_id != encounter.monsters[1].combatant_id


def test_legacy_ranged_fixture_still_proves_backline_classification() -> None:
    selene = build_selene_asharrow()
    assert starting_position_ft(selene, "heroes") == 0


def test_backliner_holds_only_while_active_frontline_ally_exists() -> None:
    frontline = EncounterCombatant(
        combatant_id="hero-1:karnok-stoneward-l1",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    backline = EncounterCombatant(
        combatant_id="hero-2:selene-test-fixture",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_selene_asharrow()),
    )
    monster = EncounterCombatant(
        combatant_id="monster-1:srd-goblin-warrior",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(build_goblin_warrior()),
    )
    encounter = EncounterSetup(
        heroes=[frontline, backline], monsters=[monster],
        hero_total_levels=2, monster_total_cr="1/4",
    )
    assert backline_holds_position(backline, encounter) is True
    frontline.state.current_hp = 0
    frontline.state.is_alive = False
    frontline.state.is_dead = True
    assert backline_holds_position(backline, encounter) is False


def test_melee_front_lines_begin_engaged() -> None:
    encounter = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    assert abs(encounter.heroes[0].position_ft - encounter.monsters[0].position_ft) == 5


def test_duplicate_canonical_cards_receive_independent_runtime_state() -> None:
    encounter = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "karnok-stoneward-l1"],
        monster_ids=["srd-goblin-warrior"],
    ))
    first, second = encounter.heroes
    assert first.combatant_id != second.combatant_id
    first.state.current_hp = 1
    first.state.resources[0].current_uses = 0
    assert second.state.current_hp == second.state.template.max_hp
    assert second.state.resources[0].current_uses == 2


def test_selection_allows_at_most_six_cards_per_side() -> None:
    six_heroes = ["karnok-stoneward-l1"] * 6
    six_monsters = ["srd-goblin-warrior"] * 6
    encounter = build_encounter_setup(EncounterSelection(hero_ids=six_heroes, monster_ids=six_monsters))
    assert len(encounter.heroes) == 6
    assert len(encounter.monsters) == 6
    assert encounter.hero_total_levels == 6
    assert encounter.monster_total_cr == "3/2"
    with pytest.raises(ValidationError):
        EncounterSelection(hero_ids=six_heroes + ["karnok-stoneward-l1"], monster_ids=six_monsters)
    with pytest.raises(ValidationError):
        EncounterSelection(hero_ids=six_heroes, monster_ids=six_monsters + ["srd-goblin-warrior"])


def test_unknown_card_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown monster card"):
        build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-l1"], monster_ids=["not-a-real-monster"],
        ))
