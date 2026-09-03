from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.combat.state import build_combatant_state
from app.content.pregens import build_selene_asharrow
from app.domain.encounters import EncounterCombatant
from app.domain.models import EncounterSelection


def test_nearest_targeting_uses_distance_not_frontline_backline_roles() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-bandit"],
    ))
    archer = build_selene_asharrow()
    setup.heroes[1] = EncounterCombatant(
        combatant_id=f"hero-2:{archer.id}",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(archer),
    )
    near, far = setup.heroes
    attacker = setup.monsters[0]

    assert near.position_ft == 5
    assert far.position_ft == 0
    assert attacker.position_ft == 10
    assert select_nearest_target(attacker, setup).combatant_id == near.combatant_id

    near.state.current_hp = 0
    near.state.is_alive = False
    near.state.is_dead = True

    assert select_nearest_target(attacker, setup).combatant_id == far.combatant_id
