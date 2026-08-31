from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.opening_burst import opening_burst_available, wins_initiative_over_all_enemies
from app.domain.models import EncounterSelection


def _setup():
    return build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-boar"],
    ))


def test_opening_burst_requires_strict_win_over_every_enemy() -> None:
    setup = _setup()
    boar = setup.monsters[0]
    setup.heroes[0].state.initiative_total = 14
    setup.heroes[1].state.initiative_total = 16
    boar.state.initiative_total = 15
    assert wins_initiative_over_all_enemies(boar, setup) is False

    boar.state.initiative_total = 17
    assert wins_initiative_over_all_enemies(boar, setup) is True


def test_opening_burst_tie_and_later_round_fail_closed() -> None:
    setup = _setup()
    boar = setup.monsters[0]
    for hero in setup.heroes:
        hero.state.initiative_total = 15
    boar.state.initiative_total = 15
    assert opening_burst_available(1, boar, setup) is False

    boar.state.initiative_total = 20
    assert opening_burst_available(2, boar, setup) is False


def test_saber_tooth_running_leap_marks_only_first_multiattack_strike() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-saber-toothed-tiger"],
    ))
    hero, saber = setup.heroes[0], setup.monsters[0]
    hero.state.initiative_total = 10
    saber.state.initiative_total = 20

    events, _ = resolve_combat_turn(
        1, 1, saber, hero, setup, FixedDiceProvider([15, 1, 1, 15, 1, 1]),
    )

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 2
    assert attacks[0].feature_id == "running-leap"
    assert attacks[1].feature_id == "saber-toothed-tiger-multiattack"
