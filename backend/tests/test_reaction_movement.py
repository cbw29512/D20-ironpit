from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.reaction_movement import move_toward_with_reactions
from app.combat.state import begin_turn
from app.domain.models import EncounterSelection


def _three_way(reactor_id: str = "srd-commoner"):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=[reactor_id, "srd-commoner"],
        starting_distance_ft=5,
    ))
    mover, reactor, target = setup.heroes[0], setup.monsters[0], setup.monsters[1]
    mover.position_ft, reactor.position_ft, target.position_ft = 5, 0, 30
    begin_turn(mover.state)
    return setup, mover, reactor, target


def test_departure_reaction_resolves_before_movement_then_move_completes() -> None:
    setup, mover, reactor, target = _three_way()
    events, sequence, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]),
    )
    assert [event.event_type for event in events] == ["attack", "movement"]
    assert events[0].feature_id == "opportunity-attack"
    assert events[0].sequence == 1 and events[1].sequence == 2 and sequence == 3
    assert reactor.state.reaction_available is False
    assert movement is events[1]
    assert mover.position_ft == 25


def test_creature_being_approached_does_not_get_opportunity_attack() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"], starting_distance_ft=30,
    ))
    mover, target = setup.heroes[0], setup.monsters[0]
    begin_turn(mover.state)
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]),
    )
    assert [event.event_type for event in events] == ["movement"]
    assert target.state.reaction_available is True
    assert movement is not None


def test_grappling_opportunity_attack_stops_move_before_position_changes() -> None:
    setup, mover, reactor, target = _three_way("srd-crocodile")
    before = mover.position_ft
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([19, 1]),
    )
    assert len(events) == 1 and events[0].feature_id == "opportunity-attack"
    assert movement is None
    assert mover.position_ft == before
    assert "grappled" in mover.state.active_effect_ids
    assert "restrained" in mover.state.active_effect_ids


def test_forced_movement_uses_same_pipeline_without_provoking() -> None:
    setup, mover, reactor, target = _three_way()
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]), movement_source="forced",
    )
    assert [event.event_type for event in events] == ["movement"]
    assert movement is not None
    assert reactor.state.reaction_available is True
