from __future__ import annotations

import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType


def _fighter(*, mastered: bool = True):
    template = build_karnok_stoneward().model_copy(
        update={"weapon_masteries": ["greatsword"] if mastered else []},
        deep=True,
    )
    return build_combatant_state(template)


def _target(
    *,
    resistance: bool = False,
    vulnerability: bool = False,
    immunity: bool = False,
):
    template = build_goblin_warrior().model_copy(
        update={
            "armor_class": 30,
            "damage_resistances": [DamageType.SLASHING] if resistance else [],
            "damage_vulnerabilities": [DamageType.SLASHING] if vulnerability else [],
            "damage_immunities": [DamageType.SLASHING] if immunity else [],
        },
        deep=True,
    )
    return build_combatant_state(template)


def _miss(attacker, defender, attack=None):
    return resolve_attack(
        1,
        1,
        attacker,
        defender,
        attack or attacker.template.weapon_attack,
        5,
        FixedDiceProvider([1]),
        spend_action=False,
    )


def test_mastered_graze_miss_deals_attack_ability_modifier_as_typed_damage() -> None:
    fighter = _fighter()
    target = _target()
    before = target.current_hp

    event = _miss(fighter, target)

    assert event.hit is False
    assert event.damage_roll is not None and event.damage_roll.total == 3
    assert target.current_hp == before - 3
    assert event.damage_components[0].source == "Greatsword (Graze)"
    assert event.damage_components[0].damage_type is DamageType.SLASHING
    assert event.damage_components[0].rolls == []
    assert "Graze deals 3 slashing damage" in event.description


def test_graze_ignores_weapon_damage_bonus_and_other_hit_damage_math() -> None:
    fighter = _fighter()
    target = _target()
    attack = fighter.template.weapon_attack.model_copy(update={"damage_bonus": 99})

    event = _miss(fighter, target, attack)

    assert event.damage_roll is not None and event.damage_roll.total == 3
    assert event.damage_components[0].total == 3


def test_unmastered_graze_weapon_does_no_damage_on_a_miss() -> None:
    fighter = _fighter(mastered=False)
    target = _target()
    before = target.current_hp

    event = _miss(fighter, target)

    assert event.hit is False
    assert event.damage_roll is None
    assert event.damage_components == []
    assert target.current_hp == before


def test_graze_resistance_reduces_damage_but_vulnerability_does_not_increase_it() -> None:
    fighter = _fighter()
    resistant = _target(resistance=True)
    vulnerable = _target(vulnerability=True)

    resisted = _miss(fighter, resistant)
    vulnerable_event = _miss(fighter, vulnerable)

    assert resisted.damage_roll is not None and resisted.damage_roll.total == 1
    assert vulnerable_event.damage_roll is not None and vulnerable_event.damage_roll.total == 3


def test_graze_immunity_reduces_damage_to_zero() -> None:
    fighter = _fighter()
    target = _target(immunity=True)
    before = target.current_hp

    event = _miss(fighter, target)

    assert event.damage_roll is not None and event.damage_roll.total == 0
    assert event.damage_components[0].applied_total == 0
    assert target.current_hp == before


def test_graze_damage_never_goes_below_zero() -> None:
    fighter = _fighter()
    target = _target()
    attack = fighter.template.weapon_attack.model_copy(update={"attack_ability_modifier": -2})

    event = _miss(fighter, target, attack)

    assert event.damage_roll is not None and event.damage_roll.total == 0
    assert event.damage_components[0].total == 0


def test_mastered_graze_fails_closed_without_explicit_attack_ability_modifier() -> None:
    fighter = _fighter()
    target = _target()
    attack = fighter.template.weapon_attack.model_copy(update={"attack_ability_modifier": None})

    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        _miss(fighter, target, attack)
