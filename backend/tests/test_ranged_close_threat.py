from app.combat.attacks import resolve_attack
from app.combat.condition_rules import is_incapacitated
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.encounter_targeting import close_ranged_threat_exists
from app.domain.models import EncounterSelection, RollMode, WeaponAttackKind


def _setup(two_heroes: bool = False):
    hero_ids = ["karnok-stoneward-l1", "rokhan-stonefury-l1"] if two_heroes else ["karnok-stoneward-l1"]
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=hero_ids, monster_ids=["srd-scout"],
    ))
    downed = setup.heroes[0]
    downed.state.current_hp = 0
    downed.state.is_unconscious = True
    downed.state.active_effect_ids.append("prone")
    scout = setup.monsters[0]
    scout.position_ft = 10
    for hero in setup.heroes:
        hero.position_ft = 5
    ranged = next(
        attack for attack in [scout.state.template.weapon_attack, *scout.state.template.alternate_weapon_attacks]
        if attack.weapon.attack_kind is WeaponAttackKind.RANGED
    )
    return setup, scout, downed, ranged


def test_incapacitated_adjacent_target_does_not_threaten_ranged_attacker() -> None:
    setup, scout, downed, ranged = _setup()
    assert is_incapacitated(downed.state) is True
    assert close_ranged_threat_exists(scout, setup) is False

    event = resolve_attack(
        1, 1, scout.state, downed.state, ranged, 5,
        FixedDiceProvider([18, 7, 1, 1]),
        actor_event_id=scout.combatant_id,
        target_event_id=downed.combatant_id,
        close_enemy_active=close_ranged_threat_exists(scout, setup),
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE


def test_other_standing_adjacent_enemy_still_threatens_ranged_attacker() -> None:
    setup, scout, downed, ranged = _setup(two_heroes=True)
    standing = setup.heroes[1]
    assert standing.state.current_hp > 0
    assert close_ranged_threat_exists(scout, setup) is True

    event = resolve_attack(
        1, 1, scout.state, downed.state, ranged, 5,
        FixedDiceProvider([18, 7, 1, 1]),
        actor_event_id=scout.combatant_id,
        target_event_id=downed.combatant_id,
        close_enemy_active=close_ranged_threat_exists(scout, setup),
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL
