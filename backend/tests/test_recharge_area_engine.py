from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.offensive_movement_policy import choose_offensive_movement_intent
from app.combat.recharge_action_policy import recharge_action_choice
from app.combat.recharge_action_resolution import resolve_priority_recharge_action
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.actions import SavingThrowAction
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting


def _fixture(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    if side == "monsters":
        action = SavingThrowAction(
            id="recharge-area", name="Recharge Area", save_ability="dexterity", dc=15, range_ft=0,
            area=AreaTargeting(shape="cone", origin="self", length_ft=15),
            damage_dice_count=1, damage_dice_size=6, damage_type="fire", success_damage="none",
            resource_id="area-use",
        )
        template = build_goblin_warrior().model_copy(update={
            "id": "generic-recharge-area-fixture", "name": "Recharge Fixture",
            "saving_throw_actions": [action],
            "resources": [ResourceDefinition(
                id="area-use", name="Area Use", max_uses=1,
                recharge=RechargeRule(minimum_roll=5),
            )],
        })
    else:
        template = build_karnok_stoneward()
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _setup() -> tuple[EncounterCombatant, EncounterSetup]:
    actor = _fixture("actor", "monsters", 1, 5)
    first = _fixture("first", "heroes", 2, 5)
    second = _fixture("second", "heroes", 3, 5)
    setup = EncounterSetup(
        heroes=[first, second], monsters=[actor], hero_total_levels=2, monster_total_cr="1",
        map_definition=BattleMapDefinition(id="recharge-area", width_squares=24, height_squares=16),
    )
    return actor, setup


def test_recharge_policy_selects_generic_area_save_family() -> None:
    actor, setup = _setup()
    choice = recharge_action_choice(actor, setup)
    assert choice is not None
    kind, payload = choice
    assert kind == "area-save"
    action, placement = payload
    assert action.id == "recharge-area"
    assert placement.target_ids == ("first", "second")


def test_recharge_area_resolution_spends_once_and_resolves_independent_saves() -> None:
    actor, setup = _setup()
    events, sequence, handled = resolve_priority_recharge_action(
        10, 2, actor, setup, FixedDiceProvider([1, 4, 20]), "2:actor",
    )
    assert handled is True
    assert sequence == 12
    assert [event.target_id for event in events] == ["first", "second"]
    assert events[0].save_succeeded is False
    assert events[0].damage_components[0].rolls == [4]
    assert events[1].save_succeeded is True
    assert events[1].damage_components == []
    assert actor.state.action_available is False
    assert actor.state.resources[0].current_uses == 0
    assert events[0].resource_remaining == 0
    assert events[1].resource_remaining is None


def test_movement_prefers_reachable_recharge_cone_over_legal_ranged_fallback() -> None:
    actor = _fixture("actor", "monsters", 1, 5)
    target = _fixture("target", "heroes", 6, 5)
    setup = EncounterSetup(
        heroes=[target], monsters=[actor], hero_total_levels=1, monster_total_cr="1",
        map_definition=BattleMapDefinition(id="recharge-movement", width_squares=24, height_squares=16),
    )
    begin_turn(actor.state)

    intent = choose_offensive_movement_intent(actor, setup, "1:actor")

    assert intent is not None
    assert intent.target_id == "target"
    assert intent.family == "ability"
    assert intent.desired_distance_ft == 15


def test_turn_moves_for_recharge_cone_then_uses_it_before_normal_attack() -> None:
    actor = _fixture("actor", "monsters", 1, 5)
    target = _fixture("target", "heroes", 6, 5)
    setup = EncounterSetup(
        heroes=[target], monsters=[actor], hero_total_levels=1, monster_total_cr="1",
        map_definition=BattleMapDefinition(id="recharge-turn", width_squares=24, height_squares=16),
    )

    events, _ = resolve_combat_turn(1, 1, actor, target, setup, FixedDiceProvider([1, 4]))

    assert actor.state.position.x > 1
    offense = [event for event in events if event.event_type in {"attack", "saving_throw"}]
    assert len(offense) == 1
    assert offense[0].event_type == "saving_throw"
    assert offense[0].feature_id == "recharge-area"
    assert actor.state.resources[0].current_uses == 0
