from __future__ import annotations

from app.combat.attack_hit_damage import resolve_attack_hit_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.barbarian_level19_profile import build_rokhan_stonefury_level19_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType, RollMode


def _resistant_target():
    try:
        template = build_goblin_warrior().model_copy(
            update={
                "max_hp": 500,
                "damage_resistances": [DamageType.SLASHING],
            },
            deep=True,
        )
        state = build_combatant_state(template)
        state.current_hp = 500
        return state
    except Exception as exc:
        raise AssertionError("Unable to build resistant level-19 test target.") from exc


def _critical_hit(level: int, natural_roll: int):
    try:
        attacker = build_combatant_state(build_rokhan_stonefury_level(level))
        target = _resistant_target()
        result = resolve_attack_hit_damage(
            attacker,
            target,
            attacker.template.weapon_attack,
            FixedDiceProvider([1, 1, 10, 10]),
            critical=True,
            attack_mode=RollMode.NORMAL,
            turn_key=f"1:rokhan-l{level}",
            bonus_damage=None,
            affected_states=[attacker, target],
            sneak_attack_ally_available=False,
            natural_roll=natural_roll,
        )
        return result
    except Exception as exc:
        raise AssertionError(f"Unable to resolve level-{level} critical test hit.") from exc


def test_level19_binds_irresistible_offense_to_universal_grants() -> None:
    profile = build_rokhan_stonefury_level19_profile()
    template = build_rokhan_stonefury_level(19)
    features = template.progression_features

    assert profile.level == 19
    assert template.max_hp == 233
    assert template.ability_scores is not None
    assert template.ability_scores.strength == 21
    assert template.weapon_attack.attack_bonus == 11
    assert template.weapon_attack.damage_bonus == 5
    assert [item.source_id for item in features.damage_resistance_bypass_grants] == [
        "boon-irresistible-offense",
    ]
    assert set(features.damage_resistance_bypass_grants[0].damage_types) == {
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
        DamageType.SLASHING,
    }
    assert [
        (item.source_id, item.ability, item.damage_type_source)
        for item in features.natural_twenty_attack_damage_grants
    ] == [("boon-irresistible-offense", "strength", "attack")]
    assert ("barbarian", 19, "canonical") in build_certified_hero_registry()


def test_level19_ignores_slashing_resistance_and_adds_21_on_natural_20() -> None:
    result = _critical_hit(19, 20)

    assert len(result.damage_components) == 2
    base, boon = result.damage_components
    assert base.damage_type == DamageType.SLASHING
    assert base.applied_total == base.total
    assert boon.source == "Boon of Irresistible Offense"
    assert boon.damage_type == DamageType.SLASHING
    assert boon.total == 21
    assert boon.applied_total == 21


def test_level19_overwhelming_strike_requires_natural_20_not_other_critical() -> None:
    result = _critical_hit(19, 19)

    assert len(result.damage_components) == 1
    assert result.damage_components[0].applied_total == result.damage_components[0].total


def test_level18_does_not_receive_level19_resistance_bypass_or_damage_rider() -> None:
    result = _critical_hit(18, 20)

    assert len(result.damage_components) == 1
    component = result.damage_components[0]
    assert component.applied_total == component.total // 2
