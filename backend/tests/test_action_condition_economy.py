from app.combat.action_economy import is_available
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.domain.models import EncounterSelection, RollMode


def _setup(condition: str):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    attacker, defender = setup.monsters[0], setup.heroes[0]
    defender.state.active_effect_ids.append(condition)
    return attacker, defender


def test_stunned_refreshes_reaction_resource_but_cannot_use_economy_and_keeps_speed() -> None:
    _, stunned = _setup("stunned")
    stunned.state.reaction_available = False
    begin_turn(stunned.state)
    assert stunned.state.reaction_available is True
    assert all(not is_available(stunned.state, cost) for cost in ("action", "bonus_action", "reaction"))
    assert stunned.state.movement_remaining_ft == stunned.state.template.speed_ft


def test_paralyzed_blocks_economy_and_sets_speed_zero() -> None:
    _, paralyzed = _setup("paralyzed")
    begin_turn(paralyzed.state)
    assert all(not is_available(paralyzed.state, cost) for cost in ("action", "bonus_action", "reaction"))
    assert paralyzed.state.movement_remaining_ft == 0


def test_stunned_grants_attack_advantage_without_automatic_critical() -> None:
    attacker, defender = _setup("stunned")
    begin_turn(attacker.state)
    event = resolve_attack(
        1, 1, attacker.state, defender.state, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([19, 5, 1]), actor_event_id=attacker.combatant_id, target_event_id=defender.combatant_id,
    )
    assert event.attack_roll is not None and event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.hit is True
    assert event.critical is False


def test_paralyzed_grants_attack_advantage_and_close_hit_critical() -> None:
    attacker, defender = _setup("paralyzed")
    begin_turn(attacker.state)
    event = resolve_attack(
        1, 1, attacker.state, defender.state, attacker.state.template.weapon_attack, 5,
        FixedDiceProvider([19, 5, 1, 1]), actor_event_id=attacker.combatant_id, target_event_id=defender.combatant_id,
    )
    assert event.attack_roll is not None and event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.hit is True
    assert event.critical is True
