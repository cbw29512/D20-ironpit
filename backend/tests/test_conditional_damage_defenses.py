from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.damage_defense_rules import ConditionalDamageResistance
from app.domain.models import DamageType


def _target(*, silver_bypass: bool = False):
    template = build_demo_fighter().model_copy(deep=True)
    template.conditional_damage_resistances = [ConditionalDamageResistance(
        damage_types=[DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING],
        nonmagical_attack_only=True,
        bypass_if_silvered=silver_bypass,
    )]
    return build_combatant_state(template)


def _attack(*, magical: bool = False, silvered: bool = False):
    attack = build_goblin_warrior().weapon_attack.model_copy(deep=True)
    attack.weapon.magical = magical
    attack.weapon.silvered = silvered
    return attack


def test_nonmagical_physical_resistance_uses_attack_origin_metadata() -> None:
    target = _target()
    assert adjusted_damage_amount(9, DamageType.SLASHING, target, attack=_attack()) == 4
    assert adjusted_damage_amount(9, DamageType.SLASHING, target, attack=_attack(magical=True)) == 9
    assert adjusted_damage_amount(9, DamageType.SLASHING, target) == 9
    assert adjusted_damage_amount(9, DamageType.FIRE, target, attack=_attack()) == 9


def test_silvered_weapon_bypasses_only_when_rule_allows_it() -> None:
    assert adjusted_damage_amount(
        9, DamageType.SLASHING, _target(silver_bypass=True), attack=_attack(silvered=True)
    ) == 9
    assert adjusted_damage_amount(
        9, DamageType.SLASHING, _target(silver_bypass=False), attack=_attack(silvered=True)
    ) == 4
