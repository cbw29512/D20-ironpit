from __future__ import annotations

from app.combat.resource_conversion import conversion_available, resolve_resource_conversion
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.models import ResourceDefinition
from app.domain.resource_conversion import ResourceConversionAction


def test_no_action_resource_conversion_preserves_action_economy() -> None:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.resources = [
        ResourceDefinition(id="source", name="Source", max_uses=2),
        ResourceDefinition(id="target", name="Target", max_uses=1),
    ]
    state = build_combatant_state(template)
    state.resources["source"].current_uses = 2
    state.resources["target"].current_uses = 0
    action = ResourceConversionAction(
        id="restore-target",
        name="Restore Target",
        action_cost="none",
        source_resource_id="source",
        source_cost=1,
        target_resource_id="target",
        target_gain=1,
    )

    assert conversion_available(state, action) is True
    event = resolve_resource_conversion(state, action, sequence=1, round_number=1, actor_id="hero")

    assert state.resources["source"].current_uses == 1
    assert state.resources["target"].current_uses == 1
    assert state.action_available is True
    assert state.bonus_action_available is True
    assert event.feature_id == "restore-target"
