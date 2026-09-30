from __future__ import annotations

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.combatants import ResourceDefinition
from app.domain.actions import AreaHealingRider, SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting


def _member(cid: str, side: str, position: int) -> EncounterCombatant:
    state = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    state.position = GridPosition(x=position // 5, y=0)
    return EncounterCombatant(
        combatant_id=cid,
        side=side,
        position_ft=position,
        state=state,
    )


def test_bonus_action_area_save_preserves_action() -> None:
    actor = _member("actor", "heroes", 0)
    target = _member("target", "monsters", 5)
    action = SavingThrowAction(
        id="fear-burst",
        name="Fear Burst",
        action_cost="bonus_action",
        save_ability="wisdom",
        dc=10,
        range_ft=0,
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=30),
    )
    actor.state.template.saving_throw_actions = [action]
    setup = EncounterSetup(
        heroes=[actor],
        monsters=[target],
        hero_total_levels=1,
        monster_total_cr="1",
        ruleset="2024",
        map_definition=BattleMapDefinition(
            id="area-save-action-cost-test",
            width_squares=10,
            height_squares=10,
        ),
    )

    selected = choose_area_save(actor, setup)
    assert selected is not None
    selected_action, placement = selected
    assert selected_action.id == action.id

    events, _ = resolve_area_save(
        1,
        1,
        actor,
        setup,
        selected_action,
        placement,
        FixedDiceProvider([20]),
    )

    assert len(events) == 1
    assert actor.state.bonus_action_available is False
    assert actor.state.action_available is True


def test_area_save_healing_rider_spends_one_action_and_resource_with_independent_rolls() -> None:
    actor = _member("actor", "heroes", 0)
    ally = _member("ally", "heroes", 5)
    enemy = _member("enemy", "monsters", 10)
    ally.state.current_hp = 1
    actor.state.template.resources = [
        ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2),
    ]
    actor.state.resources = build_combatant_state(actor.state.template).resources
    action = SavingThrowAction(
        id="lands-aid",
        name="Land's Aid",
        save_ability="constitution",
        dc=20,
        range_ft=60,
        area=AreaTargeting(shape="radius", origin="point", radius_ft=10),
        damage_dice_count=2,
        damage_dice_size=6,
        damage_type="necrotic",
        success_damage="half",
        resource_id="wild-shape",
        area_healing_rider=AreaHealingRider(dice_count=2, dice_size=6),
    )
    actor.state.template.saving_throw_actions = [action]
    setup = EncounterSetup(
        heroes=[actor, ally], monsters=[enemy], hero_total_levels=2,
        monster_total_cr="1", ruleset="2024",
        map_definition=BattleMapDefinition(id="lands-aid-test", width_squares=12, height_squares=12),
    )

    selected = choose_area_save(actor, setup)
    assert selected is not None
    selected_action, placement = selected
    events, _ = resolve_area_save(
        1, 1, actor, setup, selected_action, placement,
        FixedDiceProvider([3, 4, 1, 5, 6]),
    )

    damage = next(event for event in events if event.event_type == "saving_throw")
    healing = next(event for event in events if event.event_type == "healing")
    assert damage.damage_roll is not None and damage.damage_roll.rolls == [3, 4]
    assert healing.healing_roll is not None and healing.healing_roll.rolls == [5, 6]
    assert healing.target_id == "ally"
    assert ally.state.current_hp == 12
    assert actor.state.resources[0].current_uses == 1
    assert actor.state.action_available is False


def test_area_save_healing_rider_can_be_used_with_no_hostile_targets_if_healing_is_needed() -> None:
    actor = _member("actor", "heroes", 0)
    ally = _member("ally", "heroes", 5)
    enemy = _member("enemy", "monsters", 55)
    ally.state.current_hp = 1
    actor.state.template.resources = [
        ResourceDefinition(id="wild-shape", name="Wild Shape", max_uses=2),
    ]
    actor.state.resources = build_combatant_state(actor.state.template).resources
    action = SavingThrowAction(
        id="lands-aid",
        name="Land's Aid",
        save_ability="constitution",
        dc=13,
        range_ft=60,
        area=AreaTargeting(shape="radius", origin="point", radius_ft=10),
        damage_dice_count=2,
        damage_dice_size=6,
        damage_type="necrotic",
        success_damage="half",
        resource_id="wild-shape",
        area_healing_rider=AreaHealingRider(dice_count=2, dice_size=6),
    )
    actor.state.template.saving_throw_actions = [action]
    setup = EncounterSetup(
        heroes=[actor, ally], monsters=[enemy], hero_total_levels=2,
        monster_total_cr="1", ruleset="2024",
        map_definition=BattleMapDefinition(id="lands-aid-heal-only", width_squares=12, height_squares=12),
    )

    selected = choose_area_save(actor, setup)
    assert selected is not None
    events, _ = resolve_area_save(
        1, 1, actor, setup, selected[0], selected[1],
        FixedDiceProvider([5, 6]),
    )

    assert [event.event_type for event in events] == ["healing"]
    assert events[0].target_id == "ally"
    assert actor.state.resources[0].current_uses == 1
