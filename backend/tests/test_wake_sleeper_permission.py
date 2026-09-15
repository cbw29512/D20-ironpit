from app.combat.condition_removal_policy import removable
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.audited_fighter import build_karnok_stoneward
from app.content.basic_condition_actions import WAKE_SLEEPER_ID, wake_sleeper_action
from app.domain.encounters import EncounterCombatant


def _target() -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id="sleeping-ally",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_karnok_stoneward()),
    )


def test_wake_sleeper_rejects_unconscious_without_source_permission() -> None:
    target = _target()
    apply_timed_condition(
        target.state,
        "unconscious",
        "other-effect",
        source_effect_id="unrelated-unconscious",
        applied_round=1,
    )

    assert removable(target, wake_sleeper_action()) == []


def test_wake_sleeper_accepts_explicitly_permitted_unconscious() -> None:
    target = _target()
    apply_timed_condition(
        target.state,
        "unconscious",
        "brass-dragon",
        source_effect_id="sleep-breath",
        applied_round=1,
        allowed_removal_action_ids=[WAKE_SLEEPER_ID],
    )

    assert removable(target, wake_sleeper_action()) == ["unconscious"]
