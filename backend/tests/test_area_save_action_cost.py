from __future__ import annotations

from app.combat.area_save_actions import resolve_area_save
from app.combat.area_targeting import AreaPlacement
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.targeting import AreaTargeting


def _member(cid: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=cid,
        side=side,
        position_ft=position,
        state=build_combatant_state(build_karnok_stoneward().model_copy(deep=True)),
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
        area=AreaTargeting(shape="emanation", radius_ft=30),
    )
    actor.state.template.saving_throw_actions = [action]
    setup = EncounterSetup(heroes=[actor], monsters=[target])
    placement = AreaPlacement(origin_ft=0, target_ids=("target",), friendly_ids=())

    events, _ = resolve_area_save(1, 1, actor, setup, action, placement, FixedDiceProvider([20]))

    assert len(events) == 1
    assert actor.state.bonus_action_available is False
    assert actor.state.action_available is True
