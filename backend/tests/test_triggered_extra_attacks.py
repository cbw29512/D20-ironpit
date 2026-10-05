from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.turn_damage import clear_turn_damage
from app.combat.triggered_extra_attacks import (
    clear_regeneration_owned_stacks,
    resolve_triggered_extra_attacks_after_turn,
)
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.triggered_extra_attacks import TriggeredExtraAttackStack
from app.domain.weapons import DamageType, Weapon, WeaponAttack, WeaponAttackKind


def _rule() -> TriggeredExtraAttackStack:
    attack = WeaponAttack(
        id="attached-limb-rend",
        weapon=Weapon(
            id="attached-limb-rend-weapon",
            name="Rend",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=2,
            dice_size=4,
            damage_type=DamageType.SLASHING,
            animation="strike",
            reach_ft=5,
        ),
        attack_bonus=6,
        damage_bonus=4,
    )
    return TriggeredExtraAttackStack(
        source_id="loathsome-limbs",
        source_name="Loathsome Limbs",
        trigger_damage_type=DamageType.SLASHING,
        trigger_damage_minimum=15,
        requires_bloodied=True,
        max_stacks=4,
        max_uses=4,
        exhaustion_per_stack=1,
        attack=attack,
        clears_on_regeneration_heal=True,
    )


def _setup():
    base = build_karnok_stoneward().model_copy(update={
        "name": "Test Troll",
        "kind": "monster",
        "ruleset": "2024",
        "max_hp": 94,
        "triggered_extra_attack_stacks": [_rule()],
    }, deep=True)
    troll = EncounterCombatant(
        combatant_id="monster-1:troll",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(base),
    )
    target = EncounterCombatant(
        combatant_id="hero-1:target",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_karnok_stoneward().model_copy(update={"max_hp": 200}, deep=True)),
    )
    return troll, target, EncounterSetup(heroes=[target], monsters=[troll], hero_total_levels=1, monster_total_cr="5")


def test_trigger_requires_bloodied_and_fifteen_slashing(monkeypatch) -> None:
    troll, _target, setup = _setup()
    calls = []

    def fake_attack(sequence, round_number, attacker, target, attack, distance, dice, setup, **kwargs):
        calls.append(attack.id)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack",
            actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            attack_id=attack.id, attack_name=attack.weapon.name, animation="strike",
            description="attached attack",
        )

    monkeypatch.setattr("app.combat.triggered_extra_attacks.resolve_encounter_attack", fake_attack)

    troll.state.current_hp = 60
    troll.state.damage_taken_this_turn_by_type = {"slashing": 15}
    events, _ = resolve_triggered_extra_attacks_after_turn(1, 1, troll, setup, FixedDiceProvider([10]))
    assert events == []
    assert troll.state.exhaustion_level == 0

    troll.state.current_hp = 40
    troll.state.damage_taken_this_turn_by_type = {"slashing": 14}
    events, _ = resolve_triggered_extra_attacks_after_turn(1, 1, troll, setup, FixedDiceProvider([10]))
    assert events == []

    troll.state.damage_taken_this_turn_by_type = {"slashing": 15}
    events, _ = resolve_triggered_extra_attacks_after_turn(1, 1, troll, setup, FixedDiceProvider([10]))
    assert [event.event_type for event in events] == ["feature", "attack"]
    assert troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"] == 1
    assert troll.state.feature_use_counts["loathsome-limbs"] == 1
    assert troll.state.exhaustion_level == 1
    assert calls == ["attached-limb-rend"]


def test_stacks_add_one_attack_each_and_cap_at_four(monkeypatch) -> None:
    troll, _target, setup = _setup()
    calls = []

    def fake_attack(sequence, round_number, attacker, target, attack, distance, dice, setup, **kwargs):
        calls.append(attack.id)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack",
            actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            attack_id=attack.id, attack_name=attack.weapon.name, animation="strike",
            description="attached attack",
        )

    monkeypatch.setattr("app.combat.triggered_extra_attacks.resolve_encounter_attack", fake_attack)
    troll.state.current_hp = 40
    for expected in range(1, 5):
        troll.state.damage_taken_this_turn_by_type = {"slashing": 20}
        calls.clear()
        resolve_triggered_extra_attacks_after_turn(1, expected, troll, setup, FixedDiceProvider([10]))
        assert troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"] == expected
        assert troll.state.exhaustion_level == expected
        assert len(calls) == expected

    troll.state.damage_taken_this_turn_by_type = {"slashing": 20}
    calls.clear()
    resolve_triggered_extra_attacks_after_turn(1, 5, troll, setup, FixedDiceProvider([10]))
    assert troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"] == 4
    assert troll.state.feature_use_counts["loathsome-limbs"] == 4
    assert troll.state.exhaustion_level == 4
    assert len(calls) == 4


def test_trigger_checks_every_owner_after_any_turn(monkeypatch) -> None:
    troll, target, setup = _setup()
    calls = []

    def fake_attack(sequence, round_number, attacker, target, attack, distance, dice, setup, **kwargs):
        calls.append((attacker.combatant_id, attack.id))
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="attack",
            actor_id=attacker.combatant_id, actor_name=attacker.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            attack_id=attack.id, attack_name=attack.weapon.name, animation="strike",
            description="attached attack",
        )

    monkeypatch.setattr("app.combat.triggered_extra_attacks.resolve_encounter_attack", fake_attack)
    troll.state.current_hp = 40
    troll.state.damage_taken_this_turn_by_type = {"slashing": 15}

    events, sequence = resolve_triggered_extra_attacks_after_turn(
        1, 1, target, setup, FixedDiceProvider([10]),
    )
    assert [event.event_type for event in events] == ["feature"]
    assert troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"] == 1
    assert calls == []

    clear_turn_damage(setup)
    assert troll.state.damage_taken_this_turn_by_type == {}
    assert target.state.damage_taken_this_turn_by_type == {}

    events, _ = resolve_triggered_extra_attacks_after_turn(
        sequence, 1, troll, setup, FixedDiceProvider([10]),
    )
    assert [event.event_type for event in events] == ["attack"]
    assert troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"] == 1
    assert calls == [(troll.combatant_id, "attached-limb-rend")]


def test_regeneration_clear_removes_only_source_owned_exhaustion() -> None:
    troll, _target, _setup = _setup()
    troll.state.triggered_extra_attack_stack_counts["loathsome-limbs"] = 2
    troll.state.source_owned_exhaustion_levels["loathsome-limbs"] = 2
    troll.state.exhaustion_level = 3
    cleared = clear_regeneration_owned_stacks(troll.state)
    assert cleared == [("Loathsome Limbs", 2)]
    assert troll.state.exhaustion_level == 1
    assert "loathsome-limbs" not in troll.state.triggered_extra_attack_stack_counts
    assert "loathsome-limbs" not in troll.state.source_owned_exhaustion_levels
