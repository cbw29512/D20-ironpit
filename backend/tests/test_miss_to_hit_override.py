from __future__ import annotations

from app.combat.miss_to_hit_override import apply_miss_to_hit_override
from app.combat.state import begin_turn, build_combatant_state
from app.content.rogue_thief_2014_runtime import build_mara_quickstep_2014
from app.domain.progression import MissToHitOverrideGrant, ProgressionCombatFeatures


def test_resource_backed_miss_to_hit_override_preserves_stroke_of_luck() -> None:
    template = build_mara_quickstep_2014(20)
    state = build_combatant_state(template)

    hit, source_id, source_name = apply_miss_to_hit_override(state, hit=False)

    assert (hit, source_id, source_name) == (True, "stroke-of-luck", "Stroke of Luck")
    assert next(item for item in state.resources if item.id == "stroke-of-luck").current_uses == 0
    assert apply_miss_to_hit_override(state, hit=False) == (False, None, None)


def test_turn_start_refresh_policy_tracks_runtime_state_not_active_turn_identity() -> None:
    template = build_mara_quickstep_2014(1)
    features = ProgressionCombatFeatures(
        miss_to_hit_override_grants=[
            MissToHitOverrideGrant(
                source_id="test-peerless-aim",
                source_name="Test Peerless Aim",
                usage_policy="refresh_at_turn_start",
            )
        ]
    )
    state = build_combatant_state(template.model_copy(update={"progression_features": features}))

    first = apply_miss_to_hit_override(state, hit=False)
    second_before_refresh = apply_miss_to_hit_override(state, hit=False)

    assert first == (True, "test-peerless-aim", "Test Peerless Aim")
    assert state.turn_start_feature_cooldowns == ["test-peerless-aim"]
    assert second_before_refresh == (False, None, None)

    begin_turn(state)

    assert state.turn_start_feature_cooldowns == []
    assert apply_miss_to_hit_override(state, hit=False) == (
        True, "test-peerless-aim", "Test Peerless Aim",
    )
