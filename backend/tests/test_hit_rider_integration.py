"""Exercise real attack dispatch, rather than calling the rider directly."""
import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.damage_reaction_events import damage_event_chain
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


class HitAndSaveDice:
    def roll(self, sides):
        return 19 if sides == 20 else 1


def fixture(immune=False):
    hero = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=0,
        state=build_combatant_state(build_kael_stillwater_2024(5)),
    )
    template = build_goblin_warrior().model_copy(update={
        "max_hp": 1000, "saving_throw_bonuses": {"constitution": 0},
        "damage_immunities": [DamageType.BLUDGEONING] if immune else [],
    })
    target = EncounterCombatant(
        combatant_id="foe", side="monsters", position_ft=5,
        state=build_combatant_state(template),
    )
    setup = EncounterSetup(heroes=[hero], monsters=[target], hero_total_levels=5, monster_total_cr="0")
    return hero, target, setup


def focus(hero):
    return next(item.current_uses for item in hero.state.resources if item.id == "focus-points")


def test_extra_attack_emits_hit_then_rider_once_per_turn():
    hero, _, setup = fixture()
    events, sequence = resolve_attack_action(1, 1, hero, setup, HitAndSaveDice())
    assert [event.sequence for event in events] == [1, 2, 3]
    assert [event.event_type for event in events] == ["attack", "feature", "attack"]
    assert events[1].feature_id == "stunning-strike"
    assert events[0].attack_id == "kael-2024-unarmed"
    assert sequence == 4
    assert focus(hero) == 4


@pytest.mark.parametrize("immune", [False, True])
def test_opportunity_hit_rider_uses_active_turn_even_when_damage_is_zero(immune):
    hero, target, setup = fixture(immune)
    _, sequence = resolve_attack_action(1, 1, hero, setup, HitAndSaveDice())
    event = resolve_opportunity_attack(
        sequence, 1, hero, target, setup, 5, 10, "speed", HitAndSaveDice(), turn_key="1:foe",
    )
    assert event is not None and event.hit
    if immune:
        assert event.hp_before == event.hp_after
    events, final = damage_event_chain(
        sequence + 1, 1, hero, event, setup, HitAndSaveDice(), turn_key="1:foe",
    )
    assert [item.event_type for item in events] == ["attack", "feature"]
    assert events[1].feature_id == "stunning-strike"
    assert final == sequence + 2
    assert focus(hero) == 3


def test_missing_active_turn_fails_before_spending_resource():
    hero, target, setup = fixture()
    event = resolve_opportunity_attack(1, 1, hero, target, setup, 5, 10, "speed", HitAndSaveDice())
    with pytest.raises(ValueError, match="active turn key"):
        damage_event_chain(2, 1, hero, event, setup, HitAndSaveDice())
    assert focus(hero) == 5


@pytest.mark.parametrize("dashes", [0, 1, 2])
def test_off_turn_speed_reduction_preserves_spent_movement_and_scales_dash(dashes):
    from app.combat.encounter_movement import grant_dash_movement
    from app.combat.state import begin_turn
    hero, target, setup = fixture()
    begin_turn(target.state)
    for _ in range(dashes):
        grant_dash_movement(target)
    target.state.movement_remaining_ft -= 10
    event = resolve_opportunity_attack(
        1, 1, hero, target, setup, 5, 10, "speed", HitAndSaveDice(), turn_key="1:foe",
    )
    damage_event_chain(2, 1, hero, event, setup, HitAndSaveDice(), turn_key="1:foe")
    assert target.state.movement_remaining_ft == 15 * (1 + dashes) - 10
    begin_turn(target.state)
    assert target.state.dash_uses_this_turn == 0
    assert target.state.movement_remaining_ft == 15


def test_grid_does_not_commit_step_when_reaction_spends_remaining_allowance():
    from app.combat.grid_reaction_movement import move_toward_on_grid
    from app.domain.grid import BattleMapDefinition, GridPosition
    hero, mover, setup = fixture()
    destination = hero.model_copy(deep=True)
    destination.combatant_id = "destination"
    destination.state.position = GridPosition(x=7, y=1)
    destination.state.reaction_available = False
    hero.state.position = GridPosition(x=0, y=1)
    mover.state.position = GridPosition(x=1, y=1)
    mover.state.movement_remaining_ft = 10  # Already spent 20 feet this turn.
    setup.heroes.append(destination)
    setup.map_definition = BattleMapDefinition(id="slow-grid", width_squares=10, height_squares=3)
    events, _, movement = move_toward_on_grid(
        1, 1, mover, destination, setup, 5, HitAndSaveDice(), turn_key="1:foe",
    )
    assert any(event.feature_id == "stunning-strike" for event in events)
    assert movement is None
    assert mover.state.position == GridPosition(x=1, y=1)
    assert mover.state.movement_remaining_ft == 0
