from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType
from app.domain.weapons import OnHitSaveDamage


def _attacker():
    state = build_combatant_state(build_karnok_stoneward().model_copy(update={"combat_traits": []}, deep=True))
    attack = state.template.weapon_attack.model_copy(update={
        "id": "save-damage-test",
        "on_hit_save_damage": OnHitSaveDamage(
            source="Venom", save_ability="constitution", dc=13,
            dice_count=2, dice_size=6, damage_type=DamageType.POISON, success_damage="half",
        ),
    }, deep=True)
    return state, attack


def _target(*, resistant: bool = False, immune: bool = False):
    source = build_goblin_warrior()
    bonuses = dict(source.saving_throw_bonuses); bonuses["constitution"] = 0
    template = source.model_copy(update={
        "armor_class": 10, "max_hp": 60, "saving_throw_bonuses": bonuses,
        "damage_resistances": [DamageType.POISON] if resistant else [],
        "damage_immunities": [DamageType.POISON] if immune else [],
    }, deep=True)
    return build_combatant_state(template)


def _hit(target, values):
    attacker, attack = _attacker()
    return resolve_attack(1, 1, attacker, target, attack, 5, FixedDiceProvider(values), spend_action=False)


def _component(event, source: str):
    return next(part for part in event.damage_components if part.source == source)


def test_failed_save_adds_full_typed_damage_to_same_hit() -> None:
    target = _target()
    event = _hit(target, [15, 4, 4, 5, 3, 3])
    venom = _component(event, "Venom")
    assert event.hit is True
    assert event.save_ability == "constitution"
    assert event.save_dc == 13
    assert event.save_succeeded is False
    assert event.saving_throw_roll is not None and event.saving_throw_roll.total == 5
    assert venom.rolls == [3, 3]
    assert venom.total == 6 and venom.applied_total == 6
    assert event.damage_roll is not None
    assert event.damage_roll.total == sum(part.applied_total for part in event.damage_components)
    assert event.hp_before - event.hp_after == event.damage_roll.total


def test_successful_save_halves_before_poison_resistance() -> None:
    target = _target(resistant=True)
    event = _hit(target, [15, 4, 4, 18, 3, 4])
    venom = _component(event, "Venom")
    assert event.save_succeeded is True
    assert venom.rolls == [3, 4]
    assert venom.total == 3
    assert venom.applied_total == 1


def test_poison_immunity_zeroes_only_poison_component() -> None:
    target = _target(immune=True)
    event = _hit(target, [15, 4, 4, 5, 6, 6])
    venom = _component(event, "Venom")
    weapon = next(part for part in event.damage_components if part.source != "Venom")
    assert venom.total == 12 and venom.applied_total == 0
    assert weapon.applied_total > 0
    assert event.hp_before - event.hp_after == weapon.applied_total


def test_critical_hit_does_not_double_save_dependent_damage_dice() -> None:
    target = _target()
    event = _hit(target, [20, 2, 2, 2, 2, 5, 4, 4])
    venom = _component(event, "Venom")
    weapon = next(part for part in event.damage_components if part.source != "Venom")
    assert event.critical is True
    assert len(weapon.rolls) == 4
    assert venom.rolls == [4, 4]
    assert len(venom.rolls) == 2
