from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.masteries import (
    apply_weapon_mastery_on_hit,
    consume_attack_roll_effects,
    resolve_attack_roll_effect_sources,
)
from app.combat.state import begin_turn, build_combatant_state, end_turn
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.equipment import build_shortbow
from app.domain.models import AttackRollEffectKind, RollMode, WeaponAttack


def build_shortbow_master():
    template = build_demo_fighter()
    template.weapon_attack = WeaponAttack(
        id="test-fighter-shortbow",
        weapon=build_shortbow(),
        attack_bonus=5,
        damage_bonus=3,
    )
    template.alternate_weapon_attacks = []
    template.weapon_masteries = ["shortbow"]
    return build_combatant_state(template)


def test_vex_applies_after_mastered_weapon_deals_damage() -> None:
    archer = build_shortbow_master()
    target = build_combatant_state(build_goblin_warrior())
    begin_turn(archer)

    event = resolve_attack(
        1, 1, archer, target, archer.template.weapon_attack, 30, FixedDiceProvider([14, 3])
    )

    assert event.hit is True
    assert event.feature_id == "vex"
    assert len(archer.attack_roll_effects) == 1
    effect = archer.attack_roll_effects[0]
    assert effect.kind is AttackRollEffectKind.ADVANTAGE
    assert effect.target_actor_id == target.template.id
    assert effect.source_turns_remaining == 2


def test_vex_grants_next_attack_advantage_then_is_consumed() -> None:
    archer = build_shortbow_master()
    target = build_combatant_state(build_goblin_warrior())
    begin_turn(archer)
    resolve_attack(
        1, 1, archer, target, archer.template.weapon_attack, 30, FixedDiceProvider([14, 3])
    )
    end_turn(archer, (archer, target))
    assert archer.attack_roll_effects[0].source_turns_remaining == 1
    begin_turn(archer)

    event = resolve_attack(
        2,
        2,
        archer,
        target,
        archer.template.weapon_attack,
        30,
        FixedDiceProvider([4, 17, 3]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.rolls == [4, 17]
    assert event.hit is True
    assert target.current_hp == 0
    assert archer.attack_roll_effects == []


def test_vex_is_specific_to_the_creature_that_was_hit() -> None:
    archer = build_shortbow_master()
    first_target = build_combatant_state(build_goblin_warrior())
    other_template = build_goblin_warrior().model_copy(
        update={"id": "other-goblin", "name": "Other Goblin"}
    )
    other_target = build_combatant_state(other_template)
    apply_weapon_mastery_on_hit(
        archer,
        first_target,
        archer.template.weapon_attack.weapon,
        damage_dealt=True,
    )

    assert resolve_attack_roll_effect_sources(archer, first_target.template.id) == (1, 0)
    assert resolve_attack_roll_effect_sources(archer, other_target.template.id) == (0, 0)
    consume_attack_roll_effects(archer, other_target.template.id)
    assert len(archer.attack_roll_effects) == 1


def test_unused_vex_expires_at_end_of_next_turn() -> None:
    archer = build_shortbow_master()
    target = build_combatant_state(build_goblin_warrior())
    begin_turn(archer)
    apply_weapon_mastery_on_hit(
        archer,
        target,
        archer.template.weapon_attack.weapon,
        damage_dealt=True,
    )

    end_turn(archer, (archer, target))
    assert archer.attack_roll_effects[0].source_turns_remaining == 1
    begin_turn(archer)
    end_turn(archer, (archer, target))
    assert archer.attack_roll_effects == []


def test_reaction_applied_vex_expires_at_end_of_immediate_next_turn() -> None:
    archer = build_shortbow_master()
    target = build_combatant_state(build_goblin_warrior())

    event = resolve_attack(
        1,
        1,
        archer,
        target,
        archer.template.weapon_attack,
        30,
        FixedDiceProvider([14, 3]),
        spend_action=False,
    )

    assert event.hit is True
    assert archer.turn_active is False
    assert archer.attack_roll_effects[0].source_turns_remaining == 1
    begin_turn(archer)
    assert len(archer.attack_roll_effects) == 1
    end_turn(archer, (archer, target))
    assert archer.attack_roll_effects == []


def test_goblin_shortbow_does_not_gain_vex_without_mastery() -> None:
    goblin = build_combatant_state(build_goblin_warrior())
    fighter = build_combatant_state(build_demo_fighter())
    shortbow = goblin.template.alternate_weapon_attacks[0]

    event = resolve_attack(1, 1, goblin, fighter, shortbow, 35, FixedDiceProvider([15, 3]))

    assert event.hit is True
    assert event.feature_id is None
    assert goblin.attack_roll_effects == []
