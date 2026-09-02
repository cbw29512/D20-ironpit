import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.light_weapons import mark_light_extra_attack_used, plan_light_extra_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.equipment import build_scimitar
from app.content.rogue_equipment import build_shortsword
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import AttackActionDefinition, AttackActionSlot, EncounterSelection, WeaponAttack


class MaxDiceProvider:
    def roll(self, sides: int) -> int:
        return sides


def _attack(attack_id, weapon, modifier=3):
    return WeaponAttack(
        id=attack_id,
        weapon=weapon,
        attack_bonus=5,
        damage_bonus=modifier,
        attack_ability="dexterity",
        attack_ability_modifier=modifier,
    )


def _state(masteries=("scimitar",), modifier=3):
    template = build_karnok_stoneward().model_copy(deep=True)
    template.weapon_attack = _attack("test-shortsword", build_shortsword(), modifier)
    template.alternate_weapon_attacks = [_attack("test-scimitar", build_scimitar(), modifier)]
    template.weapon_masteries = list(masteries)
    return build_combatant_state(template)


def test_nick_moves_nick_weapons_light_extra_attack_off_bonus_action() -> None:
    state = _state()
    plan = plan_light_extra_attack(state, state.template.weapon_attack, "1:hero")

    assert plan is not None
    assert plan.attack.weapon.id == "scimitar"
    assert plan.attack.damage_bonus == 0
    assert plan.uses_bonus_action is False
    assert plan.feature_id == "weapon-mastery-nick"


def test_nick_does_not_apply_when_nick_weapon_is_only_the_trigger_attack() -> None:
    state = _state()
    scimitar = state.template.alternate_weapon_attacks[0]
    shortsword = state.template.weapon_attack
    state.template.weapon_attack = scimitar
    state.template.alternate_weapon_attacks = [shortsword]

    plan = plan_light_extra_attack(state, scimitar, "1:hero")

    assert plan is not None
    assert plan.attack.weapon.id == "shortsword"
    assert plan.uses_bonus_action is True
    assert plan.feature_id == "light-extra-attack"


def test_two_weapon_fighting_restores_modifier_on_nick_extra_attack() -> None:
    state = _state()
    state.template.fighting_style = "Defense"
    state.template.fighting_styles = ["Defense", "Two-Weapon Fighting"]
    plan = plan_light_extra_attack(state, state.template.weapon_attack, "1:hero")

    assert plan is not None
    assert plan.attack.weapon.id == "scimitar"
    assert plan.attack.damage_bonus == 3
    assert plan.uses_bonus_action is False
    assert plan.feature_id == "weapon-mastery-nick"


def test_two_weapon_fighting_restores_modifier_without_nick_or_extra_attack_count() -> None:
    state = _state(masteries=())
    state.template.fighting_styles = ["Two-Weapon Fighting"]
    plan = plan_light_extra_attack(state, state.template.weapon_attack, "1:hero")

    assert plan is not None
    assert plan.attack.weapon.id == "scimitar"
    assert plan.attack.damage_bonus == 3
    assert plan.uses_bonus_action is True
    assert plan.feature_id == "light-extra-attack"


def test_unmastered_nick_uses_ordinary_light_bonus_action() -> None:
    state = _state(masteries=())
    plan = plan_light_extra_attack(state, state.template.weapon_attack, "1:hero")

    assert plan is not None
    assert plan.attack.damage_bonus == 0
    assert plan.uses_bonus_action is True
    assert plan.feature_id == "light-extra-attack"


def test_light_extra_attack_requires_different_light_weapon_and_is_once_per_turn() -> None:
    state = _state()
    state.template.alternate_weapon_attacks = []
    assert plan_light_extra_attack(state, state.template.weapon_attack, "1:hero") is None

    state = _state()
    mark_light_extra_attack_used(state, "1:hero")
    assert plan_light_extra_attack(state, state.template.weapon_attack, "1:hero") is None
    assert plan_light_extra_attack(state, state.template.weapon_attack, "2:hero") is not None


def test_light_extra_attack_preserves_negative_ability_modifier() -> None:
    state = _state(masteries=(), modifier=-1)
    plan = plan_light_extra_attack(state, state.template.weapon_attack, "1:hero")

    assert plan is not None
    assert plan.attack.damage_bonus == -1


def test_light_extra_attack_fails_closed_without_explicit_ability_modifier() -> None:
    state = _state()
    broken = state.template.alternate_weapon_attacks[0].model_copy(update={"attack_ability_modifier": None})
    state.template.alternate_weapon_attacks = [broken]

    with pytest.raises(ValueError, match="explicit attack ability modifier"):
        plan_light_extra_attack(state, state.template.weapon_attack, "1:hero")


def _nick_extra_attack_setup(is_attack_action=True):
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-ogre"],
    ))
    attacker = setup.heroes[0]
    attacker.position_ft = 0
    setup.monsters[0].position_ft = 5
    shortsword = _attack("test-shortsword", build_shortsword())
    scimitar = _attack("test-scimitar", build_scimitar())
    attacker.state.template.weapon_attack = shortsword
    attacker.state.template.alternate_weapon_attacks = [scimitar]
    attacker.state.template.weapon_masteries = ["scimitar"]
    attacker.state.template.attack_action = AttackActionDefinition(
        id="fighter-extra-attack",
        name="Extra Attack",
        is_attack_action=is_attack_action,
        slots=[
            AttackActionSlot(attack_ids=[shortsword.id]),
            AttackActionSlot(attack_ids=[shortsword.id]),
        ],
    )
    begin_turn(attacker.state)
    return setup, attacker


def test_nick_adds_exactly_one_attack_and_action_surge_cannot_add_another() -> None:
    setup, attacker = _nick_extra_attack_setup()
    events, sequence = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())
    attacks = [event for event in events if event.event_type == "attack"]

    assert len(attacks) == 3
    assert attacks[-1].feature_id == "weapon-mastery-nick"
    assert attacks[-1].weapon_id == "scimitar"
    assert attacker.state.bonus_action_available is True

    attacker.state.action_available = True
    more, _ = resolve_attack_action(sequence, 1, attacker, setup, MaxDiceProvider())
    assert len([event for event in more if event.event_type == "attack"]) == 2


def test_monster_style_multiattack_never_infers_nick_extra_attack() -> None:
    setup, attacker = _nick_extra_attack_setup(is_attack_action=False)
    events, _ = resolve_attack_action(1, 1, attacker, setup, MaxDiceProvider())

    assert len([event for event in events if event.event_type == "attack"]) == 2
    assert attacker.state.bonus_action_available is True
