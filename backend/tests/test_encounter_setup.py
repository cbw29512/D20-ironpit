import pytest

from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection


def test_builds_full_party_against_multiple_monsters() -> None:
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
        starting_distance_ft=30,
    ))

    assert len(encounter.heroes) == 4
    assert len(encounter.monsters) == 3
    assert [hero.position_ft for hero in encounter.heroes] == [0, 0, 0, 0]
    assert [monster.position_ft for monster in encounter.monsters] == [30, 30, 30]
    assert encounter.monsters[0].state.template.id == "srd-goblin-warrior"
    assert encounter.monsters[1].state.template.id == "srd-goblin-warrior"
    assert encounter.monsters[0].combatant_id != encounter.monsters[1].combatant_id


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


def test_unknown_card_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown monster card"):
        build_encounter_setup(EncounterSelection(
            hero_ids=["aldric-vane-l1"],
            monster_ids=["not-a-real-monster"],
        ))
