from app.combat.attacks import resolve_attack
from app.combat.damage_defenses import adjusted_damage_amount, apply_damage_defenses
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import DamageRollComponent, DamageType, TimedEffect
from app.domain.damage_sources import ConditionalDamageDefense, DamageDefenseKind, DamageSourceQualifier


def _component(amount: int, damage_type: DamageType) -> DamageRollComponent:
    return DamageRollComponent(
        source="test",
        notation=str(amount),
        rolls=[amount],
        damage_type=damage_type,
        total=amount,
    )


def test_damage_type_enum_contains_all_thirteen_2024_types() -> None:
    assert {member.value for member in DamageType} == {
        "acid",
        "bludgeoning",
        "cold",
        "fire",
        "force",
        "lightning",
        "necrotic",
        "piercing",
        "poison",
        "psychic",
        "radiant",
        "slashing",
        "thunder",
    }


def test_resistance_halves_damage_and_rounds_down() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_resistances = [DamageType.FIRE]

    assert adjusted_damage_amount(9, DamageType.FIRE, target) == 4


def test_timed_effect_owned_resistance_is_applied_without_global_state_mutation() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.timed_effects.append(TimedEffect(
        effect_id="test-buff",
        source_id="hero",
        source_effect_id="test-source",
        applied_round=1,
        expires_round=11,
        owned_damage_resistances=[DamageType.FIRE],
    ))

    assert target.temporary_damage_resistances == []
    assert adjusted_damage_amount(9, DamageType.FIRE, target) == 4
    assert adjusted_damage_amount(9, DamageType.FORCE, target) == 9


def test_timed_resistance_expires_by_removing_only_its_effect_instance() -> None:
    target = build_combatant_state(build_demo_fighter())
    fire_effect = TimedEffect(
        effect_id="fire-buff",
        source_id="hero",
        owned_damage_resistances=[DamageType.FIRE],
    )
    cold_effect = TimedEffect(
        effect_id="cold-buff",
        source_id="hero",
        owned_damage_resistances=[DamageType.COLD],
    )
    target.timed_effects.extend([fire_effect, cold_effect])

    target.timed_effects.remove(fire_effect)

    assert adjusted_damage_amount(8, DamageType.FIRE, target) == 8
    assert adjusted_damage_amount(8, DamageType.COLD, target) == 4


def test_vulnerability_doubles_damage() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_vulnerabilities = [DamageType.COLD]

    assert adjusted_damage_amount(9, DamageType.COLD, target) == 18


def test_immunity_reduces_matching_damage_to_zero() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_immunities = [DamageType.POISON]

    assert adjusted_damage_amount(9, DamageType.POISON, target) == 0


def test_resistance_applies_before_vulnerability_for_same_type() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_resistances = [DamageType.FIRE]
    target.template.damage_vulnerabilities = [DamageType.FIRE]

    assert adjusted_damage_amount(9, DamageType.FIRE, target) == 8


def test_mixed_damage_is_adjusted_per_component() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.damage_resistances = [DamageType.FIRE]

    applied, components = apply_damage_defenses(
        target,
        [
            _component(7, DamageType.SLASHING),
            _component(8, DamageType.FIRE),
        ],
    )

    assert applied == 11
    assert [component.total for component in components] == [7, 8]
    assert [component.applied_total for component in components] == [7, 4]


def test_immune_critical_at_zero_causes_no_death_save_failure() -> None:
    attacker = build_combatant_state(build_goblin_warrior())
    defender = build_combatant_state(build_demo_fighter())
    apply_damage(defender, defender.current_hp)
    defender.template.damage_immunities = [DamageType.FIRE]
    fire_attack = attacker.template.weapon_attack.model_copy(deep=True)
    fire_attack.weapon.damage_type = DamageType.FIRE
    fire_attack.conditional_damage = []

    event = resolve_attack(
        1,
        1,
        attacker,
        defender,
        fire_attack,
        5,
        FixedDiceProvider([20, 19, 6, 6]),
    )

    assert event.critical is True
    assert event.damage_roll is not None
    assert event.damage_components[0].total == 14
    assert event.damage_components[0].applied_total == 0
    assert event.damage_roll.total == 0
    assert defender.death_save_failures == 0
    assert defender.is_dead is False

def test_nonmagical_attack_resistance_is_bypassed_by_magical_attack() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.conditional_damage_defenses = [ConditionalDamageDefense(
        id="nonmagical-bps-resistance",
        kind=DamageDefenseKind.RESISTANCE,
        damage_types=[DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING],
        required_source_qualifiers=[DamageSourceQualifier.ATTACK],
        forbidden_source_qualifiers=[DamageSourceQualifier.MAGICAL],
    )]

    nonmagical = {
        DamageSourceQualifier.ATTACK,
        DamageSourceQualifier.WEAPON,
        DamageSourceQualifier.MELEE,
    }
    magical = {*nonmagical, DamageSourceQualifier.MAGICAL}

    assert adjusted_damage_amount(
        9, DamageType.BLUDGEONING, target, source_qualifiers=nonmagical,
    ) == 4
    assert adjusted_damage_amount(
        9, DamageType.BLUDGEONING, target, source_qualifiers=magical,
    ) == 9


def test_component_source_qualifiers_drive_conditional_defense() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.template.conditional_damage_defenses = [ConditionalDamageDefense(
        id="nonmagical-slashing-immunity",
        kind=DamageDefenseKind.IMMUNITY,
        damage_types=[DamageType.SLASHING],
        required_source_qualifiers=[DamageSourceQualifier.ATTACK],
        forbidden_source_qualifiers=[DamageSourceQualifier.MAGICAL],
    )]
    component = _component(7, DamageType.SLASHING).model_copy(update={
        "source_qualifiers": [
            DamageSourceQualifier.ATTACK,
            DamageSourceQualifier.WEAPON,
            DamageSourceQualifier.MELEE,
        ],
    })

    applied, adjusted = apply_damage_defenses(target, [component])

    assert applied == 0
    assert adjusted[0].applied_total == 0
