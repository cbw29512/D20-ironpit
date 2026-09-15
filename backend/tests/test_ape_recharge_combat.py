from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import combatant_distance
from app.combat.resources import resource_state
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


def _ape_fixture():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-ape"],
    ))
    hero, ape = setup.heroes[0], setup.monsters[0]
    hero.state.position = GridPosition(x=0, y=6)
    ape.state.position = GridPosition(x=5, y=6)
    hero.state.initiative_total = 10
    ape.state.initiative_total = 20
    return setup, hero, ape


def test_ape_rock_spends_recharge_then_failed_roll_falls_back_to_two_fists() -> None:
    setup, hero, ape = _ape_fixture()
    rock_resource = resource_state(ape.state, "ape-rock-recharge")
    assert rock_resource.current_uses == 1

    first_turn, sequence = resolve_combat_turn(
        1,
        1,
        ape,
        hero,
        setup,
        FixedDiceProvider([15, 1, 1]),
    )

    first_attacks = [event for event in first_turn if event.event_type == "attack"]
    assert len(first_attacks) == 1
    assert first_attacks[0].weapon_id == "ape-rock"
    assert first_attacks[0].hit is True
    assert rock_resource.current_uses == 0
    assert not [event for event in first_turn if event.resource_roll is not None]
    assert combatant_distance(ape, hero) == 25

    second_turn, _ = resolve_combat_turn(
        sequence,
        2,
        ape,
        hero,
        setup,
        FixedDiceProvider([5, 10, 10]),
    )

    recharge_events = [event for event in second_turn if event.resource_roll is not None]
    assert len(recharge_events) == 1
    assert recharge_events[0].resource_roll.selected_roll == 5
    assert recharge_events[0].resource_remaining == 0
    assert rock_resource.current_uses == 0

    second_attacks = [event for event in second_turn if event.event_type == "attack"]
    assert [event.weapon_id for event in second_attacks] == ["ape-fist", "ape-fist"]
    assert combatant_distance(ape, hero) == 5
