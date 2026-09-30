from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.persistent_barriers import (
    GridBarrierEdge,
    PersistentBarrierSectionState,
    PersistentBarrierState,
)

MAP = BattleMapDefinition(id="save-push", width_squares=8, height_squares=8)


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(update={"id": combatant_id, "name": combatant_id})
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _action() -> SavingThrowAction:
    return SavingThrowAction(
        id="test-wave",
        name="Test Wave",
        save_ability="constitution",
        dc=40,
        range_ft=15,
        failed_save_push_ft=10,
        magical_effect=True,
    )


def test_failed_save_push_uses_universal_forced_movement() -> None:
    actor = _member("actor", "heroes", 1, 1)
    target = _member("target", "monsters", 2, 1)
    setup = EncounterSetup(
        heroes=[actor],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1/4",
        map_definition=MAP,
    )

    event = resolve_save_action(
        1, 1, actor, target, _action(), 5, FixedDiceProvider([1]), setup=setup,
    )

    assert event.save_succeeded is False
    assert target.state.position == GridPosition(x=4, y=1)
    assert "pushed 10 feet away" in event.description


def test_failed_save_push_stops_at_live_persistent_barrier() -> None:
    actor = _member("actor", "heroes", 1, 1)
    target = _member("target", "monsters", 2, 1)
    barrier = PersistentBarrierState(
        barrier_id="wall",
        source_id="actor",
        source_side="heroes",
        action_id="test-wall",
        action_name="Test Wall",
        applied_round=1,
        expires_round=11,
        sections=[
            PersistentBarrierSectionState(
                section_id="panel-1",
                edges=[
                    GridBarrierEdge(
                        first=GridPosition(x=3, y=1),
                        second=GridPosition(x=4, y=1),
                    )
                ],
                current_hp=10,
                armor_class=15,
            )
        ],
    )
    setup = EncounterSetup(
        heroes=[actor],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1/4",
        map_definition=MAP,
        persistent_barriers=[barrier],
    )

    event = resolve_save_action(
        1, 1, actor, target, _action(), 5, FixedDiceProvider([1]), setup=setup,
    )

    assert target.state.position == GridPosition(x=3, y=1)
    assert "pushed 5 feet away" in event.description
