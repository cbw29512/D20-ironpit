from app.combat.encounter_targeting import combatant_distance
from app.combat.formation import starting_position_ft
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSelection


def _member(combatant_id: str, side: str, template) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=starting_position_ft(template, side),
        state=build_combatant_state(template),
    )


def test_fixed_pit_replaces_legacy_ninety_foot_starting_distance() -> None:
    assert "starting_distance_ft" not in EncounterSelection.model_fields
    fighter = _member("hero-1", "heroes", build_demo_fighter())
    goblin = _member("monster-1", "monsters", build_goblin_warrior())

    assert fighter.position_ft == 5
    assert goblin.position_ft == 10
    assert combatant_distance(fighter, goblin) == 5
