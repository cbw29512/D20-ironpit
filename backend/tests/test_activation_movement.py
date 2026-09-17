from app.combat.activation_movement import resolve_activation_movement
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(build_karnok_stoneward()),
    )


def test_activation_movement_grants_extra_movement_without_spending_normal_budget() -> None:
    mover = _member("hero", "heroes", 0)
    target = _member("monster", "monsters", 60)
    setup = EncounterSetup(heroes=[mover], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    normal_remaining = mover.state.movement_remaining_ft

    events, sequence = resolve_activation_movement(
        1, 1, mover, setup, FixedDiceProvider([10]), speed_fraction=0.5,
    )

    assert sequence == 2
    assert mover.position_ft == 15
    assert mover.state.movement_remaining_ft == normal_remaining
    assert len(events) == 1
    assert events[0].event_type == "movement"


def test_activation_movement_fails_closed_on_invalid_fraction() -> None:
    mover = _member("hero", "heroes", 0)
    target = _member("monster", "monsters", 60)
    setup = EncounterSetup(heroes=[mover], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    try:
        resolve_activation_movement(1, 1, mover, setup, FixedDiceProvider([10]), speed_fraction=1.5)
    except ValueError as exc:
        assert "speed_fraction" in str(exc)
    else:
        raise AssertionError("Invalid activation movement fraction must fail closed.")
