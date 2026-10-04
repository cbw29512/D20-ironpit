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


def test_voluntary_leave_from_melee_is_blocked_and_does_not_spend_the_reaction() -> None:
    setup, mover, reactor, target = _three_way()
    before = mover.state.position.model_copy(deep=True)
    events, sequence, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]),
    )

    assert events == []
    assert sequence == 1
    assert movement is None
    assert mover.state.position == before
    assert reactor.state.reaction_available is True


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
    assert movement.distance_after_ft == 5


def test_grappling_opportunity_attack_cannot_fire_when_the_pit_blocks_the_leave() -> None:
    setup, mover, reactor, target = _three_way("srd-crocodile")
    reactor.state.position = GridPosition(x=8, y=5)
    before = mover.state.position.model_copy(deep=True)
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([19, 1]),
    )

    assert events == []
    assert movement is None
    assert mover.state.position == before
    assert "grappled" not in mover.state.active_effect_ids
    assert reactor.state.reaction_available is True


def test_forced_movement_uses_same_grid_pipeline_without_provoking() -> None:
    setup, mover, reactor, target = _three_way()
    events, _, movement = move_toward_with_reactions(
        1, 1, mover, target, setup, 5, FixedDiceProvider([2]), movement_source="forced",
    )

    assert events and all(event.event_type == "movement" for event in events)
    assert sum(event.movement_ft or 0 for event in events) == 30
    assert movement is events[-1]
    assert reactor.state.reaction_available is True
