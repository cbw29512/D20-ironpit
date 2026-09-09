import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.domain.grid import GridPosition
from app.domain.models import AttackActionDefinition, AttackActionSlot, EncounterSelection, RollMode, WeaponAttackKind


class MaxDiceProvider:
    def roll(self, sides: int) -> int:
        return sides


def _extra_attack_setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner", "srd-commoner"],
    ))
    attacker = setup.heroes[0]
    attacker.state.position = GridPosition(x=7, y=6)
    setup.monsters[0].state.position = GridPosition(x=8, y=6)
    setup.monsters[1].state.position = GridPosition(x=7, y=7)
    attacker.state.template.attack_action = AttackActionDefinition(
        id="fighter-extra-attack",
        name="Extra Attack",
        slots=[
            AttackActionSlot(attack_ids=["karnok-greatsword"]),
            AttackActionSlot(attack_ids=["karnok-greatsword"]),
        ],
    )
    begin_turn(attacker.state)
    return setup, attacker


def _mixed_attack_setup(distance_ft: int):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-bandit"],
    ))
    attacker = setup.monsters[0]
    setup.heroes[0].state.position = GridPosition(x=0, y=6)
    attacker.state.position = GridPosition(x=distance_ft // 5, y=6)
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


def test_attack_action_never_invents_movement_between_legal_slots() -> None:
    setup, attacker = _extra_attack_setup()
    before = [member.state.position.model_copy(deep=True) for member in [attacker, *setup.monsters]]

    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    assert len([event for event in events if event.event_type == "attack"]) == 2
    assert not any(event.event_type in {"movement", "dash"} for event in events)
    assert [member.state.position for member in [attacker, *setup.monsters]] == before


def test_distant_melee_multiattack_preserves_action_when_no_slot_is_legal() -> None:
    setup, attacker = _extra_attack_setup()
    setup.monsters[0].state.position = GridPosition(x=20, y=5)
    setup.monsters[1].state.position = GridPosition(x=20, y=7)

    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    assert not [event for event in events if event.event_type == "attack"]
    assert not any(event.event_type in {"movement", "dash"} for event in events)
    assert attacker.state.action_available is True


def test_mixed_multiattack_uses_ranged_when_melee_is_not_legal() -> None:
    setup, attacker = _mixed_attack_setup(30)
    events, _ = resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([10, 4, 10, 4]))

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 2
    assert [event.weapon_id for event in attacks] == ["light-crossbow", "light-crossbow"]
    assert not any(event.event_type in {"movement", "dash"} for event in events)


def test_mixed_multiattack_stays_melee_when_engaged() -> None:
    setup, attacker = _mixed_attack_setup(5)
    events, _ = resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([10, 4, 10, 4]))

    attacks = [event for event in events if event.event_type == "attack"]
    assert len(attacks) == 2
    assert [event.weapon_id for event in attacks] == ["scimitar", "scimitar"]


def _ranged_split_setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1", "mara-quickstep-l1"], monster_ids=["srd-bandit"],
    ))
    attacker = setup.monsters[0]
    frontline, backline = setup.heroes
    attacker.state.position = GridPosition(x=8, y=6)
    frontline.state.position = GridPosition(x=7, y=6)
    backline.state.position = GridPosition(x=3, y=6)
    ranged = next(
        attack for attack in [backline.state.template.weapon_attack, *backline.state.template.alternate_weapon_attacks]
        if attack.weapon.attack_kind is WeaponAttackKind.RANGED
    )
    current_primary = backline.state.template.weapon_attack
    backline.state.template.weapon_attack = ranged
    backline.state.template.alternate_weapon_attacks = [
        attack for attack in [current_primary, *backline.state.template.alternate_weapon_attacks]
        if attack.id != ranged.id
    ]
    attacker.state.template.attack_action = AttackActionDefinition(
        id="mixed-multiattack",
        name="Mixed Multiattack",
        slots=[
            AttackActionSlot(attack_ids=["bandit-scimitar", "bandit-light-crossbow"]),
            AttackActionSlot(attack_ids=["bandit-scimitar", "bandit-light-crossbow"]),
        ],
    )
    begin_turn(attacker.state)
    return setup, attacker, frontline, backline


def test_mixed_multiattack_uses_one_ranged_backline_shot_on_76_to_100() -> None:
    setup, attacker, frontline, backline = _ranged_split_setup()

    events, _ = resolve_attack_action(
        1, 1, attacker, setup, FixedDiceProvider([76, 12, 4, 12, 4]),
    )
    attacks = [event for event in events if event.event_type == "attack"]

    assert [event.weapon_id for event in attacks] == ["scimitar", "light-crossbow"]
    assert attacks[0].target_id == frontline.combatant_id
    assert attacks[1].target_id == backline.combatant_id
    assert attacks[1].attack_roll is not None
    assert attacks[1].attack_roll.mode is RollMode.NORMAL


def test_mixed_multiattack_keeps_all_attacks_melee_on_1_to_75() -> None:
    setup, attacker, frontline, _backline = _ranged_split_setup()

    events, _ = resolve_attack_action(
        1, 1, attacker, setup, FixedDiceProvider([75, 12, 4, 12, 4]),
    )
    attacks = [event for event in events if event.event_type == "attack"]

    assert [event.weapon_id for event in attacks] == ["scimitar", "scimitar"]
    assert all(event.target_id == frontline.combatant_id for event in attacks)


def test_giant_constrictor_snake_multiattack_is_bite_then_constrict() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-giant-constrictor-snake"],
    ))
    attacker, target = setup.monsters[0], setup.heroes[0]
    attacker.state.position = GridPosition(x=8, y=6)
    target.state.position = GridPosition(x=7, y=7)
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
    attacker.state.position = GridPosition(x=8, y=6)
    setup.heroes[0].state.position = GridPosition(x=7, y=6)
    setup.heroes[1].state.position = GridPosition(x=11, y=6)
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
            AttackActionSlot(attack_ids=["karnok-greatsword"]),
        ],
    )

    with pytest.raises(ValueError, match="Unknown Multiattack IDs"):
        resolve_attack_action(1, 1, attacker, setup, FixedDiceProvider([10]))
