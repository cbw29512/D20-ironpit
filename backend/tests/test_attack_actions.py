import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.domain.models import AttackActionDefinition, AttackActionSlot, EncounterSelection


class MaxDiceProvider:
    def roll(self, sides: int) -> int:
        return sides


def _extra_attack_setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1"],
        monster_ids=["srd-commoner", "srd-commoner"],
        starting_distance_ft=30,
    ))
    attacker = setup.heroes[0]
    attacker.state.template.attack_action = AttackActionDefinition(
        id="fighter-extra-attack",
        name="Extra Attack",
        slots=[
            AttackActionSlot(attack_ids=["aldric-longsword"]),
            AttackActionSlot(attack_ids=["aldric-longsword"]),
        ],
    )
    begin_turn(attacker.state)
    return setup, attacker


def test_one_attack_action_pays_for_two_strikes_and_retargets() -> None:
    setup, attacker = _extra_attack_setup()
    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 2
    assert attacker.state.action_available is False
    assert [event.target_id for event in attacks] == [
        "monster-1:srd-commoner",
        "monster-2:srd-commoner",
    ]
    assert all(monster.state.current_hp == 0 for monster in setup.monsters)


def test_attack_action_can_spend_remaining_movement_between_attacks() -> None:
    setup, attacker = _extra_attack_setup()
    setup.monsters[1].position_ft = 35

    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    movements = [event for event in events if event.event_type == "movement"]
    attacks = [event for event in events if event.event_type == "attack"]
    assert [event.movement_ft for event in movements] == [25, 5]
    assert len(attacks) == 2
    assert attacker.state.movement_remaining_ft == 0


def test_unreachable_first_attack_dashes_instead_of_half_using_attack_action() -> None:
    setup, attacker = _extra_attack_setup()
    setup.starting_distance_ft = 100
    setup.monsters[0].position_ft = 100
    setup.monsters[1].position_ft = 100

    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    assert any(event.event_type == "dash" for event in events)
    assert not any(event.event_type == "attack" for event in events)
    assert attacker.state.action_available is False


def test_attack_action_fails_closed_on_unknown_attack_id() -> None:
    setup, attacker = _extra_attack_setup()
    attacker.state.template.attack_action = AttackActionDefinition(
        id="bad-action",
        name="Bad Action",
        slots=[
            AttackActionSlot(attack_ids=["not-real"]),
            AttackActionSlot(attack_ids=["aldric-longsword"]),
        ],
    )

    with pytest.raises(ValueError, match="Unknown attack IDs"):
        resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([10]))
