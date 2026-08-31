from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.domain.models import EncounterSelection


def test_frontline_protects_backline_until_frontline_falls() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "selene-asharrow-l1"],
        monster_ids=["srd-bandit"],
    ))
    front, back = setup.heroes
    attacker = setup.monsters[0]

    assert front.position_ft == 5
    assert back.position_ft == 0
    assert attacker.position_ft == 10
    assert select_nearest_target(attacker, setup).combatant_id == front.combatant_id

    front.state.current_hp = 0
    front.state.is_alive = False
    front.state.is_dead = True

    assert select_nearest_target(attacker, setup).combatant_id == back.combatant_id
