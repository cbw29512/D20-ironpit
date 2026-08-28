from app.combat.attack_actions import resolve_attack_action
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.equipment import build_scimitar
from app.content.rogue import build_demo_rogue
from app.domain.models import (
    AttackRollEffect,
    AttackRollEffectKind,
    WeaponAttack,
)


def add_advantage(state, target_id: str) -> None:
    state.attack_roll_effects.append(
        AttackRollEffect(
            id="test-advantage",
            source_actor_id="test",
            kind=AttackRollEffectKind.ADVANTAGE,
            target_actor_id=target_id,
        )
    )


def build_durable_target():
    template = build_goblin_warrior().model_copy(deep=True)
    template.max_hp = 100
    return build_combatant_state(template)


def test_demo_rogue_has_level_one_sneak_attack_and_expertise() -> None:
    rogue = build_demo_rogue()

    assert rogue.archetype == "Rogue"
    assert rogue.level == 1
    assert rogue.sneak_attack_dice_count == 1
    assert rogue.skill_bonuses["stealth"] == 7
    assert rogue.weapon_masteries == ["shortsword", "shortbow"]


def test_sneak_attack_applies_on_advantaged_ranged_hit() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    target = build_durable_target()
    shortbow = rogue.template.alternate_weapon_attacks[0]
    begin_turn(rogue, [rogue, target])
    add_advantage(rogue, target.template.id)

    event = resolve_attack(
        1, 1, rogue, target, shortbow, 60,
        FixedDiceProvider([12, 17, 4, 5]),
    )

    sneak = next(component for component in event.damage_components if component.source == "Sneak Attack")
    assert sneak.notation == "1d6+0"
    assert sneak.total == 5
    assert event.damage_roll is not None
    assert event.damage_roll.total == 12
    assert "sneak-attack" in rogue.once_per_turn_features_used


def test_sneak_attack_does_not_apply_on_normal_solo_attack() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    target = build_durable_target()
    begin_turn(rogue, [rogue, target])

    event = resolve_attack(
        1, 1, rogue, target, rogue.template.weapon_attack, 5,
        FixedDiceProvider([15, 4]),
    )

    assert all(component.source != "Sneak Attack" for component in event.damage_components)
    assert "sneak-attack" not in rogue.once_per_turn_features_used


def test_sneak_attack_requires_finesse_or_ranged_weapon() -> None:
    template = build_demo_fighter().model_copy(deep=True)
    template.sneak_attack_dice_count = 1
    attacker = build_combatant_state(template)
    target = build_durable_target()
    begin_turn(attacker, [attacker, target])
    add_advantage(attacker, target.template.id)

    event = resolve_attack(
        1, 1, attacker, target, attacker.template.weapon_attack, 5,
        FixedDiceProvider([15, 14, 4]),
    )

    assert all(component.source != "Sneak Attack" for component in event.damage_components)


def test_sneak_attack_is_only_once_with_multiple_attacks_on_same_turn() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    target = build_durable_target()
    rogue.template.alternate_weapon_attacks = [
        WeaponAttack(
            id="rogue-scimitar",
            weapon=build_scimitar(),
            attack_bonus=5,
            ability_damage_modifier=3,
        )
    ]
    begin_turn(rogue, [rogue, target])
    add_advantage(rogue, target.template.id)

    events, _ = resolve_attack_action(
        1, 1, rogue, target, rogue.template.weapon_attack, 5,
        FixedDiceProvider([15, 14, 2, 3, 13, 12, 4]),
    )

    sneak_components = [
        component
        for event in events
        for component in event.damage_components
        if component.source == "Sneak Attack"
    ]
    assert len(events) == 2
    assert len(sneak_components) == 1


def test_sneak_attack_resets_when_another_creatures_turn_begins() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    target = build_durable_target()
    begin_turn(rogue, [rogue, target])
    add_advantage(rogue, target.template.id)
    first = resolve_attack(
        1, 1, rogue, target, rogue.template.weapon_attack, 5,
        FixedDiceProvider([15, 14, 3, 2]),
    )
    assert any(component.source == "Sneak Attack" for component in first.damage_components)

    begin_turn(target, [rogue, target])
    assert "sneak-attack" not in rogue.once_per_turn_features_used
    add_advantage(rogue, target.template.id)
    reaction = resolve_attack(
        2, 1, rogue, target, rogue.template.weapon_attack, 5,
        FixedDiceProvider([15, 14, 3, 4]),
        spend_action=False,
    )

    assert any(component.source == "Sneak Attack" for component in reaction.damage_components)


def test_critical_hit_doubles_sneak_attack_dice() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    target = build_durable_target()
    begin_turn(rogue, [rogue, target])
    add_advantage(rogue, target.template.id)

    event = resolve_attack(
        1, 1, rogue, target, rogue.template.weapon_attack, 5,
        FixedDiceProvider([20, 5, 1, 2, 3, 4]),
    )

    sneak = next(component for component in event.damage_components if component.source == "Sneak Attack")
    assert event.critical is True
    assert sneak.notation == "2d6+0"
    assert sneak.rolls == [3, 4]
