from __future__ import annotations

from app.combat.area_save_actions import resolve_area_save_action
from app.combat.dice import FixedDiceProvider
from app.combat.save_targets import resolve_save_targets
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.runtime import ResourceState
from app.domain.targeting import AreaTargeting


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_karnok_stoneward() if side == "heroes" else build_goblin_warrior()
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _setup(actor: EncounterCombatant, targets: list[EncounterCombatant]) -> EncounterSetup:
    return EncounterSetup(
        heroes=[actor],
        monsters=targets,
        hero_total_levels=1,
        monster_total_cr="1",
        map_definition=BattleMapDefinition(id="save-area-test", width_squares=24, height_squares=16),
    )


def _action(**updates) -> SavingThrowAction:
    values = {
        "id": "test-breath",
        "name": "Test Breath",
        "save_ability": "dexterity",
        "dc": 15,
        "range_ft": 0,
        "damage_dice_count": 1,
        "damage_dice_size": 6,
        "damage_type": "fire",
        "success_damage": "none",
    }
    values.update(updates)
    return SavingThrowAction(**values)


def test_first_zero_damage_success_still_establishes_one_shared_damage_roll() -> None:
    actor = _member("actor", "heroes", 1, 5)
    first = _member("first", "monsters", 2, 5)
    second = _member("second", "monsters", 3, 5)
    events, next_sequence = resolve_save_targets(
        1,
        1,
        actor,
        _setup(actor, [first, second]),
        _action(),
        ("first", "second"),
        FixedDiceProvider([20, 4, 1]),
        skip_range_check=True,
    )
    assert next_sequence == 3
    assert events[0].save_succeeded is True
    assert events[0].damage_components == []
    assert events[1].save_succeeded is False
    assert events[1].damage_components[0].rolls == [4]


def test_area_save_spends_one_action_and_one_resource_for_multiple_targets() -> None:
    actor = _member("actor", "heroes", 1, 5)
    actor.state.resources.append(ResourceState(id="breath-use", name="Breath", current_uses=1, max_uses=1))
    first = _member("first", "monsters", 2, 5)
    second = _member("second", "monsters", 3, 5)
    action = _action(
        resource_id="breath-use",
        area=AreaTargeting(shape="cone", origin="self", length_ft=15),
    )
    events, next_sequence, placement = resolve_area_save_action(
        10,
        2,
        actor,
        _setup(actor, [first, second]),
        action,
        FixedDiceProvider([1, 4, 20]),
    )
    assert placement.target_ids == ("first", "second")
    assert len(events) == 2
    assert next_sequence == 12
    assert actor.state.action_available is False
    assert actor.state.resources[0].current_uses == 0
    assert events[0].resource_remaining == 0
    assert events[1].resource_remaining is None
    assert events[0].damage_components[0].rolls == [4]
    assert events[1].damage_components == []


def test_multi_target_save_rejects_allies_and_duplicate_targets_before_rolling() -> None:
    actor = _member("actor", "heroes", 1, 5)
    ally = _member("ally", "heroes", 2, 5)
    enemy = _member("enemy", "monsters", 3, 5)
    setup = EncounterSetup(
        heroes=[actor, ally], monsters=[enemy], hero_total_levels=2, monster_total_cr="1",
        map_definition=BattleMapDefinition(id="save-area-test", width_squares=24, height_squares=16),
    )
    for target_ids in (("ally",), ("enemy", "enemy")):
        try:
            resolve_save_targets(1, 1, actor, setup, _action(), target_ids, FixedDiceProvider([10]), skip_range_check=True)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Illegal target set was accepted: {target_ids}")
