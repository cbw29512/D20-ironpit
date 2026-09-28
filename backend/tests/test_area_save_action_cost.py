from __future__ import annotations

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.actions import SavingThrowAction
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
