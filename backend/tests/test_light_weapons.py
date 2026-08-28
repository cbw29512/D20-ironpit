from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.light_weapons import resolve_light_extra_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.content.equipment import build_scimitar, build_shortsword
from app.domain.models import WeaponAttack, WeaponProperty


def build_dual_wielder(*, nick: bool = False, style: str | None = None):
    template = build_demo_fighter().model_copy(deep=True)
    template.id = "dual-wielder"
    template.name = "Dual Wielder"
    template.weapon_attack = WeaponAttack(
        id="main-shortsword",
        weapon=build_shortsword(),
        attack_bonus=5,
        ability_damage_modifier=3,
    )
    template.alternate_weapon_attacks = [
        WeaponAttack(
            id="offhand-scimitar",
            weapon=build_scimitar(),
            attack_bonus=5,
            ability_damage_modifier=3,
        )
    ]
    template.weapon_masteries = ["scimitar"] if nick else []
    template.fighting_style = style
    return build_combatant_state(template)


def test_light_weapon_metadata_matches_srd_records() -> None:
    scimitar = build_scimitar()
    shortsword = build_shortsword()

    assert WeaponProperty.LIGHT in scimitar.properties
    assert WeaponProperty.FINESSE in scimitar.properties
    assert scimitar.mastery_property == "nick"
    assert WeaponProperty.LIGHT in shortsword.properties
    assert WeaponProperty.FINESSE in shortsword.properties
    assert shortsword.mastery_property == "vex"


def test_light_extra_attack_spends_bonus_action_and_drops_positive_modifier() -> None:
    attacker = build_dual_wielder()
    defender = build_combatant_state(build_goblin_warrior())
    begin_turn(attacker)

    events, _ = resolve_attack_action(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([15, 2, 15, 4]),
    )

    assert len(events) == 2
    assert events[1].feature_id == "light"
    assert events[1].weapon_id == "scimitar"
    assert events[1].damage_roll is not None
    assert events[1].damage_roll.modifier == 0
    assert events[1].damage_roll.total == 4
    assert attacker.bonus_action_available is False
    assert attacker.light_extra_attack_used is True


def test_nick_moves_light_extra_attack_into_action_without_spending_bonus_action() -> None:
    attacker = build_dual_wielder(nick=True)
    defender = build_combatant_state(build_goblin_warrior())
    begin_turn(attacker)

    events, _ = resolve_attack_action(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([15, 1, 15, 4]),
    )

    assert len(events) == 2
    assert events[1].feature_id == "nick"
    assert events[1].weapon_id == "scimitar"
    assert events[1].damage_roll is not None
    assert events[1].damage_roll.modifier == 0
    assert attacker.bonus_action_available is True
    assert attacker.light_extra_attack_used is True


def test_two_weapon_fighting_restores_ability_modifier_to_light_extra_damage() -> None:
    attacker = build_dual_wielder(style="two-weapon-fighting")
    defender = build_combatant_state(build_goblin_warrior())
    begin_turn(attacker)

    events, _ = resolve_attack_action(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([15, 1, 15, 4]),
    )

    assert events[1].damage_roll is not None
    assert events[1].damage_roll.modifier == 3
    assert events[1].damage_roll.total == 7
    assert attacker.bonus_action_available is False


def test_light_extra_attack_is_limited_to_once_per_turn() -> None:
    attacker = build_dual_wielder(nick=True)
    defender = build_combatant_state(build_goblin_warrior())
    begin_turn(attacker)
    trigger = attacker.template.weapon_attack

    first = resolve_light_extra_attack(
        1, 1, attacker, defender, trigger, 5, FixedDiceProvider([15, 3])
    )
    second = resolve_light_extra_attack(
        2, 1, attacker, defender, trigger, 5, FixedDiceProvider([15, 3])
    )

    assert first is not None
    assert second is None
    begin_turn(attacker)
    assert attacker.light_extra_attack_used is False


def test_light_extra_attack_requires_a_different_configured_light_weapon() -> None:
    attacker = build_dual_wielder()
    attacker.template.alternate_weapon_attacks = []
    defender = build_combatant_state(build_goblin_warrior())
    begin_turn(attacker)

    events, _ = resolve_attack_action(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([15, 2]),
    )

    assert len(events) == 1
    assert attacker.bonus_action_available is True
    assert attacker.light_extra_attack_used is False


def test_nick_is_mastery_gated() -> None:
    attacker = build_dual_wielder(nick=False)
    defender = build_combatant_state(build_goblin_warrior())
    begin_turn(attacker)

    events, _ = resolve_attack_action(
        1,
        1,
        attacker,
        defender,
        attacker.template.weapon_attack,
        5,
        FixedDiceProvider([15, 1, 15, 4]),
    )

    assert events[1].feature_id == "light"
    assert attacker.bonus_action_available is False
