import pytest
from pydantic import ValidationError

from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection


def test_builds_full_party_in_fixed_front_and_back_lines() -> None:
    encounter = build_encounter_setup(EncounterSelection(
        hero_ids=[
            "aldric-vane-l1",
            "brom-ironmark-l1",
            "selene-asharrow-l1",
            "mara-quickstep-l1",
        ],
        monster_ids=[
            "srd-goblin-warrior",
            "srd-goblin-warrior",
            "srd-guard",
        ],
    ))

    assert len(encounter.heroes) == 4
    assert len(encounter.monsters) == 3
    assert encounter.hero_total_levels == 4
    assert encounter.monster_total_cr == "5/8"
    assert [hero.position_ft for hero in encounter.heroes] == [5, 5, 0, 5]
    assert [monster.position_ft for monster in encounter.monsters] == [10, 10, 10]
    assert "starting_distance_ft" not in encounter.model_dump()
    assert encounter.monsters[0].state.template.id == "srd-goblin-warrior"
    assert encounter.monsters[1].state.template.id == "srd-goblin-warrior"
    assert encounter.monsters[0].combatant_id != encounter.monsters[1].combatant_id


def test_dedicated_ranged_pregen_starts_in_back_line() -> None:
    encounter = build_encounter_setup(EncounterSelection(
        hero_ids=["selene-asharrow-l1"], monster_ids=["srd-commoner"],
    ))
    assert encounter.heroes[0].position_ft == 0
    assert encounter.monsters[0].position_ft == 10


def test_melee_front_lines_begin_engaged() -> None:
    encounter = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    assert abs(encounter.heroes[0].position_ft - encounter.monsters[0].position_ft) == 5


def test_duplicate_cards_receive_independent_runtime_state() -> None:
    encounter = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1", "aldric-vane-l1"],
        monster_ids=["srd-goblin-warrior"],
    ))

    first, second = encounter.heroes
    assert first.combatant_id != second.combatant_id
    first.state.current_hp = 1
    first.state.resources[0].current_uses = 0
    assert second.state.current_hp == second.state.template.max_hp
    assert second.state.resources[0].current_uses == 2


def test_selection_allows_at_most_six_cards_per_side() -> None:
    six_heroes = ["aldric-vane-l1"] * 6
    six_monsters = ["srd-goblin-warrior"] * 6
    selection = EncounterSelection(hero_ids=six_heroes, monster_ids=six_monsters)
    encounter = build_encounter_setup(selection)

    assert len(encounter.heroes) == 6
    assert len(encounter.monsters) == 6
    assert encounter.hero_total_levels == 6
    assert encounter.monster_total_cr == "3/2"

    with pytest.raises(ValidationError):
        EncounterSelection(hero_ids=six_heroes + ["aldric-vane-l1"], monster_ids=six_monsters)
    with pytest.raises(ValidationError):
        EncounterSelection(hero_ids=six_heroes, monster_ids=six_monsters + ["srd-goblin-warrior"])


def test_unknown_card_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown monster card"):
        build_encounter_setup(EncounterSelection(
            hero_ids=["aldric-vane-l1"], monster_ids=["not-a-real-monster"],
        ))
