import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.resources import resolve_start_turn_recharges
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.encounters import EncounterCombatant
from app.domain.models import SavingThrowAction


def _recharge_member() -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(deep=True)
    template.ruleset = "2014"
    template.resources = [
        ResourceDefinition(
            id="fire-breath", name="Fire Breath", max_uses=1,
            recharge=RechargeRule(minimum_roll=5),
        )
    ]
    return EncounterCombatant(
        combatant_id="monster-1:recharge",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(template),
    )


def test_recharge_rolls_only_while_resource_is_expended() -> None:
    member = _recharge_member()
    resource = member.state.resources[0]

    full_events, sequence = resolve_start_turn_recharges(
        1, 1, member.combatant_id, member.state, FixedDiceProvider([1]),
    )
    assert full_events == []
    assert sequence == 1
    assert resource.current_uses == 1

    resource.current_uses = 0
    failed, sequence = resolve_start_turn_recharges(
        1, 2, member.combatant_id, member.state, FixedDiceProvider([4]),
    )
    assert len(failed) == 1
    assert failed[0].resource_roll.selected_roll == 4
    assert failed[0].resource_remaining == 0
    assert resource.current_uses == 0
    assert sequence == 2

    recovered, sequence = resolve_start_turn_recharges(
        sequence, 3, member.combatant_id, member.state, FixedDiceProvider([5]),
    )
    assert len(recovered) == 1
    assert recovered[0].resource_roll.selected_roll == 5
    assert recovered[0].resource_remaining == 1
    assert resource.current_uses == 1
    assert sequence == 3


def test_resource_backed_save_action_spends_on_use_and_cannot_repeat_until_recharged() -> None:
    actor = _recharge_member()
    target_template = build_goblin_warrior().model_copy(deep=True)
    target = EncounterCombatant(
        combatant_id="hero-1:target", side="heroes", position_ft=0,
        state=build_combatant_state(target_template),
    )
    action = SavingThrowAction(
        id="fire-breath", name="Fire Breath", save_ability="dexterity", dc=20,
        range_ft=30, resource_id="fire-breath", resource_cost=1,
    )

    event = resolve_save_action(
        1, 1, actor, target, action, 5, FixedDiceProvider([10]),
    )
    assert event.resource_remaining == 0
    assert actor.state.resources[0].current_uses == 0

    actor.state.action_available = True
    with pytest.raises(ValueError, match="resource is unavailable"):
        resolve_save_action(2, 1, actor, target, action, 5, FixedDiceProvider([10]))
