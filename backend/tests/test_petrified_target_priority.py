from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.domain.models import EncounterSelection


def _setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1", "brom-ironmark-l1"],
        monster_ids=["srd-commoner"],
        starting_distance_ft=30,
    ))
    petrified, active = setup.heroes
    attacker = setup.monsters[0]
    petrified.position_ft = 25
    active.position_ft = 0
    petrified.state.active_effect_ids.append("petrified")
    return setup, attacker, petrified, active


def test_petrified_enemy_is_ignored_while_non_petrified_enemy_remains() -> None:
    setup, attacker, petrified, active = _setup()
    assert abs(attacker.position_ft - petrified.position_ft) < abs(attacker.position_ft - active.position_ft)
    assert select_nearest_target(attacker, setup) is active


def test_petrified_enemy_becomes_target_after_other_active_enemies_are_down() -> None:
    setup, attacker, petrified, active = _setup()
    active.state.current_hp = 0
    active.state.is_unconscious = True
    active.state.is_stable = False
    assert select_nearest_target(attacker, setup) is petrified


def test_petrified_enemy_remains_a_legal_target_until_zero_hp_rules_remove_it() -> None:
    setup, attacker, petrified, active = _setup()
    active.state.is_alive = False
    active.state.is_dead = True
    active.state.current_hp = 0
    assert petrified.state.current_hp > 0
    assert select_nearest_target(attacker, setup) is petrified
