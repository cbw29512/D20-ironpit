from app.combat.repeat_save_transition import resolve_repeat_save_transition
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.basic_condition_actions import WAKE_SLEEPER_ID
from app.content.certified_heroes import build_karnok_stoneward


def test_failed_repeat_save_escalates_to_wakeable_timed_unconscious() -> None:
    state = build_combatant_state(build_karnok_stoneward())
    apply_timed_condition(
        state,
        "incapacitated",
        "brass-dragon",
        source_effect_id="sleep-breath",
        applied_round=1,
        repeat_save_ability="constitution",
        repeat_save_dc=14,
        repeat_save_timing="target_turn_end",
        repeat_save_failure_condition="unconscious",
        repeat_save_failure_continues=False,
        repeat_save_failure_duration_rounds=10,
        repeat_save_failure_ends_on_damage=True,
        repeat_save_failure_allowed_removal_action_ids=[WAKE_SLEEPER_ID],
    )
    original = state.timed_effects[0]

    removed, applied = resolve_repeat_save_transition(state, original, False, 2)

    assert removed == ["incapacitated"]
    assert applied == ["unconscious"]
    effect = next(item for item in state.timed_effects if item.effect_id == "unconscious")
    assert effect.repeat_save_ability is None
    assert effect.repeat_save_dc is None
    assert effect.repeat_save_timing is None
    assert effect.expires_round == 12
    assert effect.expiry_timing == "target_turn_end"
    assert effect.ends_on_damage is True
    assert effect.allowed_removal_action_ids == [WAKE_SLEEPER_ID]
