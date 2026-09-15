from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.domain.models import AttackActionDefinition, AttackActionSlot, EncounterSelection, RollMode


def test_hit_push_changes_follow_up_ranged_close_threat_math() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-bandit"],
    ))
    attacker, target = setup.monsters[0], setup.heroes[0]
    attacker.state.position = None
    target.state.position = None
    # Keep the scalar test away from the arena boundary so a push away is not clamped.
    attacker.position_ft = 20
    target.position_ft = 15
    attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
    melee = next(attack for attack in attacks if attack.id == "bandit-scimitar")
    melee.push_target_away_ft = 10
    attacker.state.template.attack_action = AttackActionDefinition(
        id="push-then-shoot",
        name="Push then Shoot",
        slots=[
            AttackActionSlot(attack_ids=["bandit-scimitar"]),
            AttackActionSlot(attack_ids=["bandit-light-crossbow"]),
        ],
    )
    begin_turn(attacker.state)

    events, _ = resolve_attack_action(
        1, 1, attacker, setup, FixedDiceProvider([15, 1, 10, 1]),
    )
    attacks = [event for event in events if event.event_type == "attack"]

    assert len(attacks) == 2
    assert attacks[0].hit is True
    assert attacks[0].distance_before_ft == 5
    assert attacks[0].distance_after_ft == 15
    assert abs(target.position_ft - attacker.position_ft) == 15
    assert attacks[1].attack_roll is not None
    assert attacks[1].attack_roll.mode is RollMode.NORMAL


def test_missed_push_does_not_change_follow_up_ranged_disadvantage() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-bandit"],
    ))
    attacker, target = setup.monsters[0], setup.heroes[0]
    attacker.state.position = None
    target.state.position = None
    attacker.position_ft = 20
    target.position_ft = 15
    attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
    next(attack for attack in attacks if attack.id == "bandit-scimitar").push_target_away_ft = 10
    attacker.state.template.attack_action = AttackActionDefinition(
        id="push-then-shoot",
        name="Push then Shoot",
        slots=[AttackActionSlot(attack_ids=["bandit-scimitar"]), AttackActionSlot(attack_ids=["bandit-light-crossbow"])],
    )
    begin_turn(attacker.state)

    # A natural 1 intentionally ends the Iron Pit turn, so use a normal miss here to
    # prove that a missed push leaves close-range disadvantage in force.
    events, _ = resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([2, 10, 10, 1]))
    attacks = [event for event in events if event.event_type == "attack"]

    assert len(attacks) == 2
    assert attacks[0].hit is False
    assert abs(target.position_ft - attacker.position_ft) == 5
    assert attacks[1].attack_roll is not None
    assert attacks[1].attack_roll.mode is RollMode.DISADVANTAGE
