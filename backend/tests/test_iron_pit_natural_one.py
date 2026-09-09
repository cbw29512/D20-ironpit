from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_action_surge import resolve_action_surge_attack
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_setup import build_encounter_setup
from app.combat.opportunity_attacks import resolve_opportunity_attack
from app.combat.state import begin_turn
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


def _setup(monster_id: str = "srd-commoner", hero_id: str = "karnok-stoneward-l1"):
    setup = build_encounter_setup(EncounterSelection(hero_ids=[hero_id], monster_ids=[monster_id]))
    return setup, setup.monsters[0], setup.heroes[0]


def test_on_turn_natural_one_terminates_voluntary_turn_resources() -> None:
    setup, attacker, target = _setup()
    begin_turn(attacker.state)
    event = resolve_encounter_attack(
        1, 1, attacker, target, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([1]), setup,
    )

    assert event.hit is False
    assert event.attack_roll is not None and event.attack_roll.selected_roll == 1
    assert event.turn_terminated is True
    assert event.turn_termination_reason == "iron-pit-natural-1-attack"
    assert attacker.state.turn_terminated is True
    assert attacker.state.action_available is False
    assert attacker.state.bonus_action_available is False
    assert attacker.state.movement_remaining_ft == 0
    assert attacker.state.reaction_available is True
    assert "immediately ends the attacker's turn" in event.description


def test_begin_turn_clears_natural_one_termination() -> None:
    setup, attacker, target = _setup()
    begin_turn(attacker.state)
    resolve_encounter_attack(
        1, 1, attacker, target, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([1]), setup,
    )
    assert attacker.state.turn_terminated is True

    begin_turn(attacker.state)
    assert attacker.state.turn_terminated is False
    assert attacker.state.turn_termination_reason is None
    assert attacker.state.action_available is True
    assert attacker.state.bonus_action_available is True
    assert attacker.state.reaction_available is True
    assert attacker.state.movement_remaining_ft == attacker.state.template.speed_ft


def test_natural_one_opportunity_attack_is_off_turn_and_does_not_poison_next_turn() -> None:
    setup, reactor, mover = _setup()
    begin_turn(reactor.state)
    event = resolve_opportunity_attack(
        1, 1, reactor, mover, setup, 5, 10, "speed", FixedDiceProvider([1]),
    )

    assert event is not None
    assert event.hit is False
    assert event.attack_roll is not None and event.attack_roll.selected_roll == 1
    assert event.turn_terminated is False
    assert event.turn_termination_reason is None
    assert reactor.state.turn_terminated is False
    assert reactor.state.action_available is True
    assert reactor.state.bonus_action_available is True
    assert reactor.state.reaction_available is False
    assert "does not terminate a future turn" in event.description

    begin_turn(reactor.state)
    assert reactor.state.action_available is True
    assert reactor.state.bonus_action_available is True
    assert reactor.state.reaction_available is True


def test_natural_one_stops_remaining_multiattack_slots() -> None:
    setup, attacker, target = _setup("srd-black-bear")
    attacker.state.position = GridPosition(x=8, y=6)
    target.state.position = GridPosition(x=7, y=6)
    begin_turn(attacker.state)
    events, _ = resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([1]))

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 1
    assert attacks[0].attack_roll is not None and attacks[0].attack_roll.selected_roll == 1
    assert attacks[0].turn_terminated is True
    assert attacker.state.turn_terminated is True


def test_action_surge_cannot_restart_a_natural_one_terminated_turn() -> None:
    setup, _monster, fighter = _setup(hero_id="karnok-stoneward-l2")
    begin_turn(fighter.state)
    fighter.state.turn_terminated = True
    fighter.state.turn_termination_reason = "iron-pit-natural-1-attack"
    fighter.state.action_available = False
    fighter.state.bonus_action_available = False
    fighter.state.movement_remaining_ft = 0

    events, sequence = resolve_action_surge_attack(
        1, 1, fighter, setup, FixedDiceProvider([20]), "1:hero-1:karnok-stoneward-l2",
    )
    action_surge = next(item for item in fighter.state.resources if item.id == "action-surge")
    assert events == []
    assert sequence == 1
    assert action_surge.current_uses == 1
    assert fighter.state.turn_terminated is True
