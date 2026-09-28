from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.actions import SavingThrowAction
from app.domain.encounters import EncounterCombatant


def _member(cid: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=cid,
        side=side,
        position_ft=0,
        state=build_combatant_state(build_karnok_stoneward().model_copy(deep=True)),
    )


def test_save_action_can_spend_bonus_action_without_spending_action() -> None:
    actor = _member("actor", "heroes")
    target = _member("target", "monsters")
    action = SavingThrowAction(
        id="test-fear",
        name="Test Fear",
        action_cost="bonus_action",
        save_ability="wisdom",
        dc=10,
        range_ft=30,
    )

    resolve_save_action(1, 1, actor, target, action, 5, FixedDiceProvider([20]))

    assert actor.state.bonus_action_available is False
    assert actor.state.action_available is True


def test_save_action_defaults_to_action_for_existing_content() -> None:
    action = SavingThrowAction(
        id="legacy-save",
        name="Legacy Save",
        save_ability="dexterity",
        dc=10,
        range_ft=30,
    )
    assert action.action_cost == "action"
