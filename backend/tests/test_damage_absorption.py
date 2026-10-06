from app.combat.damage_defenses import adjusted_damage_amount, apply_damage_defenses, resolve_damage_amount
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.ranger_hunter_2024_runtime import build_rowan_ashtrail_2024
from app.domain.damage_absorption import DamageAbsorptionRule
from app.domain.models import DamageRollComponent, DamageType


def _component(amount: int, damage_type: DamageType) -> DamageRollComponent:
    return DamageRollComponent(
        source="test",
        notation=str(amount),
        rolls=[amount],
        damage_type=damage_type,
        total=amount,
    )


def _absorb(target, damage_type: DamageType) -> None:
    target.template.damage_absorptions = [
        DamageAbsorptionRule(
            source_id=f"{damage_type.value}-absorption",
            source_name=f"{damage_type.value.title()} Absorption",
            damage_type=damage_type,
        )
    ]


def test_damage_absorption_estimation_is_pure_but_resolution_heals() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.current_hp = target.template.max_hp - 10
    _absorb(target, DamageType.FIRE)

    before = target.current_hp
    assert adjusted_damage_amount(7, DamageType.FIRE, target) == 0
    assert target.current_hp == before

    applied, healed, source_name = resolve_damage_amount(7, DamageType.FIRE, target)

    assert applied == 0
    assert healed == 7
    assert source_name == "Fire Absorption"
    assert target.current_hp == before + 7


def test_damage_absorption_caps_healing_and_ignores_nonmatching_types() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.current_hp = target.template.max_hp - 3
    _absorb(target, DamageType.LIGHTNING)

    applied, healed, source_name = resolve_damage_amount(10, DamageType.LIGHTNING, target)
    assert (applied, healed, source_name) == (0, 3, "Lightning Absorption")
    assert target.current_hp == target.template.max_hp

    target.current_hp -= 5
    applied, healed, source_name = resolve_damage_amount(4, DamageType.COLD, target)
    assert (applied, healed, source_name) == (4, 0, None)


def test_component_absorption_composes_with_other_damage_types() -> None:
    target = build_combatant_state(build_demo_fighter())
    target.current_hp = target.template.max_hp - 10
    _absorb(target, DamageType.ACID)

    applied, components = apply_damage_defenses(
        target,
        [
            _component(6, DamageType.ACID),
            _component(5, DamageType.SLASHING),
        ],
    )

    assert applied == 5
    assert [component.applied_total for component in components] == [0, 5]
    assert components[0].absorption_source_name == "Acid Absorption"
    assert components[0].absorbed_healing == 6
    assert components[1].absorption_source_name is None
    assert components[1].absorbed_healing == 0
    assert target.current_hp == target.template.max_hp - 4


def test_damage_estimation_does_not_spend_incoming_resistance_reaction() -> None:
    target = build_combatant_state(build_rowan_ashtrail_2024(15))

    estimated = adjusted_damage_amount(8, DamageType.FIRE, target)

    assert estimated == 8
    assert target.reaction_available is True
    assert target.timed_effects == []


def test_actual_damage_resolution_spends_reaction_and_recomputes_resistance() -> None:
    target = build_combatant_state(build_rowan_ashtrail_2024(15))

    applied, healed, source_name = resolve_damage_amount(8, DamageType.FIRE, target)

    assert (applied, healed, source_name) == (4, 0, None)
    assert target.reaction_available is False
    assert any(
        effect.effect_id == "incoming-damage-type-resistance"
        and DamageType.FIRE in effect.owned_damage_resistances
        for effect in target.timed_effects
    )


def test_absorption_does_not_spend_incoming_resistance_reaction() -> None:
    target = build_combatant_state(build_rowan_ashtrail_2024(15))
    target.current_hp = target.template.max_hp - 5
    _absorb(target, DamageType.FIRE)

    applied, healed, source_name = resolve_damage_amount(4, DamageType.FIRE, target)

    assert (applied, healed, source_name) == (0, 4, "Fire Absorption")
    assert target.reaction_available is True
    assert target.timed_effects == []


def test_existing_resistance_does_not_spend_incoming_resistance_reaction() -> None:
    target = build_combatant_state(build_rowan_ashtrail_2024(15))
    target.template.damage_resistances = [DamageType.FIRE]

    applied, healed, source_name = resolve_damage_amount(8, DamageType.FIRE, target)

    assert (applied, healed, source_name) == (4, 0, None)
    assert target.reaction_available is True
    assert target.timed_effects == []


def test_resistance_bypass_does_not_waste_incoming_resistance_reaction() -> None:
    target = build_combatant_state(build_rowan_ashtrail_2024(15))

    applied, healed, source_name = resolve_damage_amount(
        8,
        DamageType.FIRE,
        target,
        ignored_resistance_types={DamageType.FIRE},
    )

    assert (applied, healed, source_name) == (8, 0, None)
    assert target.reaction_available is True
    assert target.timed_effects == []
