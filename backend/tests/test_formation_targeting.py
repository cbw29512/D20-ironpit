from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.combat.state import build_combatant_state
from app.content.pregens import build_selene_asharrow
from app.domain.encounters import EncounterCombatant
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


def test_nearest_targeting_uses_grid_distance_not_legacy_roles() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-bandit"],
    ))
    archer = build_selene_asharrow()
    archer_state = build_combatant_state(archer)
    archer_state.position = GridPosition(x=2, y=6)
    setup.heroes[1] = EncounterCombatant(
        combatant_id=f"hero-2:{archer.id}",
        side="heroes",
        position_ft=0,
        state=archer_state,
    )
    near, far = setup.heroes
    attacker = setup.monsters[0]
    near.state.position = GridPosition(x=7, y=6)
    attacker.state.position = GridPosition(x=8, y=6)

    assert select_nearest_target(attacker, setup).combatant_id == near.combatant_id

    near.state.current_hp = 0
    near.state.is_alive = False
    near.state.is_dead = True

    assert select_nearest_target(attacker, setup).combatant_id == far.combatant_id
