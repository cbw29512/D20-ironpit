import pytest

from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.state import build_combatant_state
from app.combat.timed_self_effects import activate_timed_self_effect, can_activate_timed_self_effect
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant
from app.domain.models import DamageType, ResourceDefinition
from app.domain.progression import TimedSelfEffectGrant


def _actor(uses: int = 4) -> EncounterCombatant:
    template = build_demo_fighter().model_copy(update={
        "resources": [ResourceDefinition(id="focus", name="Focus", max_uses=4)],
    })
    state = build_combatant_state(template)
    state.resources[0].current_uses = uses
    return EncounterCombatant(combatant_id="hero-1", side="heroes", position_ft=0, state=state)


def _grant() -> TimedSelfEffectGrant:
    return TimedSelfEffectGrant(
        source_id="test-defense",
        source_name="Test Defense",
        action_cost="action",
        resource_id="focus",
        resource_cost=4,
        duration_rounds=10,
        condition_ids=["invisible"],
        damage_resistances=["fire", "cold"],
    )


def test_activation_spends_costs_and_installs_one_source_owned_effect() -> None:
    actor = _actor()
    event = activate_timed_self_effect(actor, _grant(), round_number=3, sequence=7)

    assert actor.state.action_available is False
    assert actor.state.resources[0].current_uses == 0
    assert actor.state.active_effect_ids == ["invisible"]
    assert len(actor.state.timed_effects) == 1
    effect = actor.state.timed_effects[0]
    assert effect.source_effect_id == "test-defense"
    assert effect.applied_round == 3
    assert effect.expires_round == 13
    assert effect.owned_damage_resistances == [DamageType.FIRE, DamageType.COLD]
    assert actor.state.temporary_damage_resistances == []
    assert adjusted_damage_amount(9, DamageType.FIRE, actor.state) == 4
    assert adjusted_damage_amount(9, DamageType.FORCE, actor.state) == 9
    assert event.feature_id == "test-defense"
    assert event.resource_remaining == 0
    assert "Test Defense" in event.description


def test_insufficient_resource_is_illegal_and_does_not_spend_action() -> None:
    actor = _actor(uses=3)
    grant = _grant()

    assert can_activate_timed_self_effect(actor, grant) is False
    with pytest.raises(ValueError, match="not currently legal"):
        activate_timed_self_effect(actor, grant, round_number=1, sequence=1)

    assert actor.state.action_available is True
    assert actor.state.resources[0].current_uses == 3
    assert actor.state.timed_effects == []


def test_unavailable_action_is_illegal_and_does_not_spend_resource() -> None:
    actor = _actor()
    actor.state.action_available = False

    assert can_activate_timed_self_effect(actor, _grant()) is False
    with pytest.raises(ValueError, match="not currently legal"):
        activate_timed_self_effect(actor, _grant(), round_number=1, sequence=1)

    assert actor.state.resources[0].current_uses == 4
    assert actor.state.timed_effects == []
