from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import select_nearest_target
from app.domain.models import EncounterSelection


def _setup(condition: str):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-commoner"],
    ))
    disabled, active = setup.heroes
    attacker = setup.monsters[0]
    attacker.position_ft = 30
    disabled.position_ft = 25
    active.position_ft = 0
    disabled.state.active_effect_ids.append(condition)
    return setup, attacker, disabled, active


def test_incapacitating_conditions_remove_target_from_active_threat_priority() -> None:
    for condition in ("incapacitated", "paralyzed", "petrified", "stunned"):
        setup, attacker, disabled, active = _setup(condition)
        assert abs(attacker.position_ft - disabled.position_ft) < abs(attacker.position_ft - active.position_ft)
        assert select_nearest_target(attacker, setup) is active, condition


def test_incapacitated_enemy_becomes_target_after_other_active_enemies_are_down() -> None:
    for condition in ("incapacitated", "paralyzed", "petrified", "stunned"):
        setup, attacker, disabled, active = _setup(condition)
        active.state.current_hp = 0
        active.state.is_unconscious = True
        active.state.is_stable = False
        assert select_nearest_target(attacker, setup) is disabled, condition


def test_partial_debuffs_do_not_remove_a_creature_from_active_threat_priority() -> None:
    for condition in ("blinded", "frightened", "poisoned", "prone", "restrained"):
        setup, attacker, debuffed, active = _setup(condition)
        assert select_nearest_target(attacker, setup) is debuffed, condition
        assert abs(attacker.position_ft - debuffed.position_ft) < abs(attacker.position_ft - active.position_ft)


def test_petrified_enemy_remains_a_legal_target_until_zero_hp_rules_remove_it() -> None:
    setup, attacker, petrified, active = _setup("petrified")
    active.state.is_alive = False
    active.state.is_dead = True
    active.state.current_hp = 0
    assert petrified.state.current_hp > 0
    assert select_nearest_target(attacker, setup) is petrified
