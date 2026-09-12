from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.certified_heroes import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant


class FixedDice:
    def roll(self, sides: int) -> int:
        return 10


def test_target_timing_does_not_expire_before_configured_round() -> None:
    state = build_combatant_state(build_karnok_stoneward())
    target = EncounterCombatant(combatant_id="target", side="heroes", position_ft=0, state=state)
    apply_timed_condition(
        state,
        "unconscious",
        "source",
        source_effect_id="sleep-effect",
        applied_round=2,
        expires_round=12,
        expiry_timing="target_turn_end",
    )

    early, sequence = resolve_target_condition_timing(1, 3, target, "target_turn_end", FixedDice())
    assert early == []
    assert sequence == 1
    assert "unconscious" in state.active_effect_ids

    due, sequence = resolve_target_condition_timing(sequence, 12, target, "target_turn_end", FixedDice())
    assert len(due) == 1
    assert due[0].removed_condition_ids == ["unconscious"]
    assert sequence == 2
    assert "unconscious" not in state.active_effect_ids
