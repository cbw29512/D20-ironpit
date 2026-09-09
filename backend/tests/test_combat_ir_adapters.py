from app.content.combat_ir_adapters import attack_capability_to_ir, save_capability_to_ir
from app.content.combat_ir_reverse_adapters import attack_ir_to_capability, save_ir_to_capability
from app.domain.capability_attacks import AttackCapabilityDefinition, SaveCapabilityDefinition
from app.domain.capability_effects import ConditionEffectDefinition, DiceSpec, ProneEffectDefinition


def test_attack_capability_round_trips_without_losing_rules_data() -> None:
    attack = AttackCapabilityDefinition(
        id="spear-ranged",
        name="Spear",
        weapon_id="spear",
        attack_kind="ranged",
        attack_bonus=6,
        damage=DiceSpec(count=1, size=6, bonus=3),
        damage_type="piercing",
        animation="projectile",
        normal_range_ft=20,
        long_range_ft=60,
        projectile="spear",
        mastery_property="sap",
        light=True,
        attack_ability="dexterity",
        attack_ability_modifier=3,
        effects=[ProneEffectDefinition(max_target_size="large")],
        resource_id="spear-use",
    )
    ir = attack_capability_to_ir(attack)
    rebuilt = attack_ir_to_capability(ir)
    assert ir.targeting.range_ft == 20
    assert ir.resolution.kind == "attack_roll"
    assert ir.resolution.weapon_id == "spear"
    assert ir.resolution.mastery_property == "sap"
    assert rebuilt.model_dump() == attack.model_dump()


def test_save_capability_round_trips_damage_and_failure_control() -> None:
    action = SaveCapabilityDefinition(
        id="shockwave",
        name="Shockwave",
        save_ability="strength",
        dc=15,
        range_ft=30,
        damage=DiceSpec(count=3, size=6),
        damage_type="thunder",
        success_damage="half",
        failure_control=ConditionEffectDefinition(condition="poisoned"),
        resource_id="shockwave-use",
    )
    ir = save_capability_to_ir(action)
    rebuilt = save_ir_to_capability(ir)
    assert ir.resolution.kind == "saving_throw"
    assert ir.resolution.dc == 15
    assert ir.resolution.success_damage == "half"
    assert ir.effects[0].kind == "condition"
    assert rebuilt.model_dump() == action.model_dump()
