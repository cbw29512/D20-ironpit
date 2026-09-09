from app.combat.conditions import attack_roll_condition_sources
from app.combat.dodge import dodge_benefits_active, resolve_dodge_action
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode


def _member(combatant_id: str, *, speed_ft: int | None = None) -> EncounterCombatant:
    template = build_goblin_warrior()
    if speed_ft is not None:
        template = template.model_copy(update={"speed_ft": speed_ft})
    state = build_combatant_state(template)
    begin_turn(state)
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="monsters",
        position_ft=0,
        state=state,
    )


def test_dodge_spends_action_and_feeds_shared_roll_modes() -> None:
    dodger = _member("dodger")
    attacker = _member("attacker")

    event = resolve_dodge_action(1, 1, dodger)

    assert dodger.state.action_available is False
    assert event.feature_id == "dodge"
    assert dodge_benefits_active(dodger.state)
    assert attack_roll_condition_sources(attacker.state, dodger.state, 5)[1] == 1
    assert saving_throw_mode(dodger.state, "dexterity") is RollMode.ADVANTAGE
    assert saving_throw_mode(dodger.state, "constitution") is RollMode.NORMAL


def test_dodge_ends_at_start_of_dodgers_next_turn() -> None:
    dodger = _member("dodger")
    resolve_dodge_action(1, 1, dodger)

    begin_turn(dodger.state)

    assert dodge_benefits_active(dodger.state) is False
    assert "dodge" not in dodger.state.active_effect_ids


def test_dodge_can_be_taken_at_speed_zero_but_grants_no_benefit() -> None:
    dodger = _member("dodger", speed_ft=0)

    event = resolve_dodge_action(1, 1, dodger)

    assert event.feature_id == "dodge"
    assert dodger.state.action_available is False
    assert "dodge" in dodger.state.active_effect_ids
    assert dodge_benefits_active(dodger.state) is False
    assert saving_throw_mode(dodger.state, "dexterity") is RollMode.NORMAL
