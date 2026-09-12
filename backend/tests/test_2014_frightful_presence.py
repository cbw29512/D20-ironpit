from app.combat.area_save_actions import resolve_area_save_action
from app.combat.area_targeting import legal_area_placements
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.source_effect_immunity import source_effect_is_immune
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.actions import HitControlEffect, SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.targeting import AreaTargeting


def _member(combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(deep=True)
    template.saving_throw_bonuses = {"wisdom": 0}
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def _action() -> SavingThrowAction:
    return SavingThrowAction(
        id="frightful-presence", name="Frightful Presence",
        save_ability="wisdom", dc=19, range_ft=120,
        area=AreaTargeting(shape="emanation", origin="self", radius_ft=120),
        failure_control_effect=HitControlEffect(
            condition_id="frightened", expiry_timing="target_turn_end", duration_rounds=10,
            repeat_save_ability="wisdom", repeat_save_dc=19,
            repeat_save_timing="target_turn_end", source_effect_immunity_on_end=True,
        ),
        source_effect_immunity_on_success=True,
    )


def _setup(actor: EncounterCombatant, target: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[target], monsters=[actor], hero_total_levels=1, monster_total_cr="1/4",
        map_definition=BattleMapDefinition(id="fear-test", width_squares=30, height_squares=30),
    )


def test_frightful_presence_failure_repeats_save_and_grants_source_immunity() -> None:
    actor = _member("monster-1:dragon", "monsters", 1, 1)
    target = _member("hero-1:target", "heroes", 4, 1)
    action = _action(); setup = _setup(actor, target)
    placement = legal_area_placements(actor, setup, action.area, action.range_ft)[0]

    events, _, _ = resolve_area_save_action(
        1, 1, actor, setup, action, FixedDiceProvider([1]), placement=placement,
    )
    assert events[0].save_succeeded is False
    assert "frightened" in target.state.active_effect_ids
    effect = target.state.timed_effects[0]
    assert effect.expires_round == 11
    assert effect.repeat_save_timing == "target_turn_end"
    assert not source_effect_is_immune(target.state, actor.combatant_id, action.id)

    repeat_events, _ = resolve_target_condition_timing(
        2, 2, target, "target_turn_end", FixedDiceProvider([20]),
    )
    assert repeat_events[0].save_succeeded is True
    assert "frightened" not in target.state.active_effect_ids
    assert source_effect_is_immune(target.state, actor.combatant_id, action.id)


def test_frightful_presence_initial_success_grants_source_immunity() -> None:
    actor = _member("monster-1:dragon", "monsters", 1, 1)
    target = _member("hero-1:target", "heroes", 4, 1)
    action = _action(); setup = _setup(actor, target)
    placement = legal_area_placements(actor, setup, action.area, action.range_ft)[0]

    events, _, _ = resolve_area_save_action(
        1, 1, actor, setup, action, FixedDiceProvider([20]), placement=placement,
    )
    assert events[0].save_succeeded is True
    assert "frightened" not in target.state.active_effect_ids
    assert source_effect_is_immune(target.state, actor.combatant_id, action.id)
