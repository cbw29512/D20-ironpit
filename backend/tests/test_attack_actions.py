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
        hero_ids=["aldric-vane-l1"], monster_ids=["srd-commoner", "srd-commoner"],
    ))
    attacker = setup.heroes[0]
    attacker.position_ft = 0
    setup.monsters[0].position_ft = 30
    setup.monsters[1].position_ft = 30
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


def _mixed_attack_setup(distance_ft: int):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1"], monster_ids=["srd-bandit"],
    ))
    attacker = setup.monsters[0]
    setup.heroes[0].position_ft = 0
    attacker.position_ft = distance_ft
    attacker.state.template.attack_action = AttackActionDefinition(
        id="mixed-multiattack",
        name="Mixed Multiattack",
        slots=[
            AttackActionSlot(attack_ids=["bandit-scimitar", "bandit-light-crossbow"]),
            AttackActionSlot(attack_ids=["bandit-scimitar", "bandit-light-crossbow"]),
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
    setup.monsters[0].position_ft = 100
    setup.monsters[1].position_ft = 100

    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    assert any(event.event_type == "dash" for event in events)
    assert not any(event.event_type == "attack" for event in events)
    assert attacker.state.action_available is False


def test_dash_that_reaches_melee_still_cannot_multiattack_same_turn() -> None:
    setup, attacker = _extra_attack_setup()
    setup.monsters[0].position_ft = 50
    setup.monsters[1].position_ft = 50

    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    assert [event.event_type for event in events] == ["movement", "dash", "movement"]
    assert events[-1].distance_after_ft == 5
    assert not any(event.event_type == "attack" for event in events)
    assert attacker.state.action_available is False


def test_mixed_multiattack_uses_ranged_option_when_fixture_starts_outside_melee() -> None:
    setup, attacker = _mixed_attack_setup(30)
    events, _ = resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([10, 4, 10, 4]))

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 2
    assert [event.weapon_id for event in attacks] == ["light-crossbow", "light-crossbow"]
    assert not any(event.event_type == "movement" for event in events)


def test_mixed_multiattack_switches_to_melee_when_engaged() -> None:
    setup, attacker = _mixed_attack_setup(5)
    events, _ = resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([10, 4, 10, 4]))

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 2
    assert [event.weapon_id for event in attacks] == ["scimitar", "scimitar"]


def test_giant_constrictor_snake_multiattack_is_bite_then_constrict() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-constrictor-snake"],
    ))
    attacker, target = setup.monsters[0], setup.heroes[0]
    begin_turn(attacker.state)

    events, _ = resolve_attack_action(
        1, 1, attacker, setup, FixedDiceProvider([15, 1, 1, 1, 1, 1])
    )

    assert [event.event_type for event in events] == ["attack", "saving_throw"]
    assert events[0].weapon_id == "giant-constrictor-snake-bite"
    assert events[1].feature_id == "giant-constrictor-snake-constrict"
    assert events[1].save_ability == "strength"
    assert events[1].save_dc == 14
    assert events[1].save_succeeded is False
    assert events[1].damage_roll is not None and events[1].damage_roll.total == 6
    assert events[1].applied_condition_ids == ["grappled"]
    assert "restrained" not in target.state.active_effect_ids
    assert attacker.state.action_available is False


def test_tyrannosaurus_bite_grapple_forces_tail_to_retarget() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "rokhan-stonefury-l1"],
        monster_ids=["srd-tyrannosaurus-rex"],
    ))
    attacker = setup.monsters[0]
    begin_turn(attacker.state)

    events, _ = resolve_attack_action(
        1, 1, attacker, setup,
        FixedDiceProvider([10, 1, 1, 1, 1, 10, 1, 1, 1, 1]),
    )
    attacks = [event for event in events if event.event_type == "attack"]

    assert [event.weapon_id for event in attacks] == ["tyrannosaurus-rex-bite", "tyrannosaurus-rex-tail"]
    assert attacks[0].target_id == "hero-1:karnok-stoneward-l1"
    assert attacks[1].target_id == "hero-2:rokhan-stonefury-l1"
    bitten, tailed = setup.heroes
    assert "grappled" in bitten.state.active_effect_ids
    assert "restrained" in bitten.state.active_effect_ids
    assert any(source.source_id == attacker.combatant_id for source in bitten.state.grapple_sources)
    assert "prone" in tailed.state.active_effect_ids


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

    with pytest.raises(ValueError, match="Unknown Multiattack IDs"):
        resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([10]))
