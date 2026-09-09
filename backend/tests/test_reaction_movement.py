from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.reaction_movement import move_toward_with_reactions
from app.combat.state import begin_turn
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


def _three_way(reactor_id: str = "srd-commoner"):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=[reactor_id, "srd-commoner"],
    ))
    mover, reactor, target = setup.heroes[0], setup.monsters[0], setup.monsters[1]
    mover.state.position = GridPosition(x=7, y=6)
    reactor.state.position = GridPosition(x=8, y=6)
    target.state.position = GridPosition(x=0, y=6)
    begin_turn(mover.state)
    return setup, mover, reactor, target


def test_departure_reaction_resolves_before_square_movement_then_move_completes() -> None:
    setup, mover, reactor, target = _three_way()
    events, sequence, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]),
    )

    assert events[0].event_type == "attack"
    assert events[0].feature_id == "opportunity-attack"
    assert all(event.event_type == "movement" for event in events[1:])
    assert sum(event.movement_ft or 0 for event in events[1:]) == 30
    assert [event.sequence for event in events] == list(range(1, 8))
    assert sequence == 8
    assert reactor.state.reaction_available is False
    assert movement is events[-1]
    assert mover.state.position == GridPosition(x=1, y=6)


def test_creature_being_approached_does_not_get_opportunity_attack() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    mover, target = setup.heroes[0], setup.monsters[0]
    mover.state.position = GridPosition(x=0, y=6)
    target.state.position = GridPosition(x=6, y=6)
    begin_turn(mover.state)
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]),
    )

    assert events and all(event.event_type == "movement" for event in events)
    assert sum(event.movement_ft or 0 for event in events) == 25
    assert target.state.reaction_available is True
    assert movement is events[-1]
    assert mover.state.position == GridPosition(x=5, y=6)


def test_grappling_opportunity_attack_stops_move_before_position_changes() -> None:
    setup, mover, reactor, target = _three_way("srd-crocodile")
    reactor.state.position = GridPosition(x=8, y=5)
    before = mover.state.position.model_copy(deep=True)
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([19, 1]),
    )

    assert len(events) == 1 and events[0].feature_id == "opportunity-attack"
    assert movement is None
    assert mover.state.position == before
    assert "grappled" in mover.state.active_effect_ids
    assert "restrained" in mover.state.active_effect_ids


def test_forced_movement_uses_same_grid_pipeline_without_provoking() -> None:
    setup, mover, reactor, target = _three_way()
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]), movement_source="forced",
    )

    assert events and all(event.event_type == "movement" for event in events)
    assert sum(event.movement_ft or 0 for event in events) == 30
    assert movement is events[-1]
    assert reactor.state.reaction_available is True
