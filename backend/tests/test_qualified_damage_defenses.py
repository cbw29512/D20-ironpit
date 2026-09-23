from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.damage_defenses import QualifiedDamageDefense
from app.domain.models import DamageType


def _target(bypass_materials: list[str] | None = None):
    target = build_combatant_state(build_demo_fighter())
    target.template.qualified_damage_defenses = [
        QualifiedDamageDefense(
            kind="resistance",
            damage_types=[DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING],
            attack_only=True,
            magical=False,
            bypass_materials=bypass_materials or [],
            source_name="Damage Resistances",
            source_text="test qualified resistance",
        )
    ]
    return target


def _attack():
    return build_goblin_warrior().weapon_attack.model_copy(deep=True)


def test_nonmagical_attack_activates_qualified_resistance() -> None:
    target = _target()
    attack = _attack()

    assert attack.weapon.magical is False
    assert adjusted_damage_amount(
        9, DamageType.SLASHING, target, attack=attack,
    ) == 4


def test_magical_attack_bypasses_nonmagical_attack_resistance() -> None:
    target = _target()
    attack = _attack()
    attack.weapon.magical = True

    assert adjusted_damage_amount(
        9, DamageType.SLASHING, target, attack=attack,
    ) == 9


def test_adamantine_material_bypasses_matching_qualified_resistance() -> None:
    target = _target(["adamantine"])
    attack = _attack()
    attack.weapon.material = "adamantine"

    assert adjusted_damage_amount(
        9, DamageType.SLASHING, target, attack=attack,
    ) == 9


def test_non_attack_damage_does_not_trigger_attack_only_resistance() -> None:
    target = _target()

    assert adjusted_damage_amount(9, DamageType.SLASHING, target) == 9
