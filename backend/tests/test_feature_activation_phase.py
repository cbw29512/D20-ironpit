from app.combat.dice import FixedDiceProvider
from app.combat.feature_activation_phase import resolve_feature_activation_phase
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_level7_rage_activation_grants_pounce_without_spending_normal_movement() -> None:
    hero = _member(build_rokhan_stonefury_level(7), "rokhan", "heroes", 0)
    enemy = _member(build_karnok_stoneward(), "target", "monsters", 60)
    setup = EncounterSetup(heroes=[hero], monsters=[enemy], hero_total_levels=7, monster_total_cr="1")
    begin_turn(hero.state)
    normal_remaining = hero.state.movement_remaining_ft

    events, sequence = resolve_feature_activation_phase(
        1, 1, hero, setup, FixedDiceProvider([10]), "1:rokhan",
    )

    assert sequence > 1
    assert events[0].event_type == "rage"
    assert any(event.event_type == "movement" for event in events[1:])
    assert hero.position_ft > 0
    assert hero.state.movement_remaining_ft == normal_remaining
