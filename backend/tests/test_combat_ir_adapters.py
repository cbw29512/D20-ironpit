from app.content.combat_ir_adapters import attack_capability_to_ir, save_capability_to_ir
from app.domain.capability_attacks import AttackCapabilityDefinition, SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec, ProneEffectDefinition


def test_attack_capability_normalizes_without_losing_rules_data() -> None:
    attack = AttackCapabilityDefinition(
        id="spear-ranged",
        name="Spear",
        attack_kind="ranged",
        attack_bonus=6,
        damage=DiceSpec(count=1, size=6, bonus=3),
        damage_type="piercing",
        animation="projectile",
        normal_range_ft=20,
        long_range_ft=60,
        effects=[ProneEffectDefinition(max_target_size="large")],
        resource_id="spear-use",
    )
    ir = attack_capability_to_ir(attack)
    assert ir.targeting.range_ft == 20
    assert ir.resolution.kind == "attack_roll"
    assert ir.resolution.attack_bonus == 6
    assert ir.primary_damage is not None and ir.primary_damage.dice == attack.damage
    assert ir.effects[0].kind == "prone"
    assert ir.resource_cost is not None and ir.resource_cost.resource_id == "spear-use"


def test_save_capability_normalizes_damage_and_failure_control() -> None:
    action = SaveCapabilityDefinition(
        id="shockwave",
        name="Shockwave",
        save_ability="strength",
        dc=15,
        range_ft=30,
        damage=DiceSpec(count=3, size=6),
        damage_type="thunder",
        success_damage="half",
        failure_control=ProneEffectDefinition(max_target_size="large"),
        resource_id="shockwave-use",
    )
    ir = save_capability_to_ir(action)
    assert ir.resolution.kind == "saving_throw"
    assert ir.resolution.dc == 15
    assert ir.resolution.success_damage == "half"
    assert ir.primary_damage is not None and ir.primary_damage.damage_type.value == "thunder"
    assert ir.effects[0].kind == "prone"
    assert ir.resource_cost is not None and ir.resource_cost.amount == 1
