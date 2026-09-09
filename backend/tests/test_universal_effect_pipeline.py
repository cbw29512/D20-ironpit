from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.modifier_stack import effective_speed
from app.combat.saving_throws import resolve_save_action
from app.content.capability_attack_compiler import compile_attack
from app.domain.actions import HitControlEffect, SavingThrowAction
from app.domain.capabilities import AttackCapabilityDefinition
from app.domain.capability_effects import ConditionEffectDefinition, DiceSpec, GrappleEffectDefinition
from app.domain.hit_modifiers import HitModifierEffect
from app.domain.models import EncounterSelection
from app.domain.weapons import DamageType, WeaponAttackKind


def test_attack_compiler_preserves_multiple_persistent_effects() -> None:
    definition = AttackCapabilityDefinition(
        id="test-tentacle",
        name="Tentacle",
        attack_kind=WeaponAttackKind.MELEE,
        attack_bonus=5,
        damage=DiceSpec(count=1, size=6, bonus=3),
        damage_type=DamageType.BLUDGEONING,
        animation="slam",
        effects=[
            GrappleEffectDefinition(escape_dc=13, restrains=True),
            ConditionEffectDefinition(condition="blinded"),
        ],
    )

    attack = compile_attack(definition)

    assert len(attack.persistent_effects) == 2
    assert attack.persistent_effects[0].grapple_escape_dc == 13
    assert attack.persistent_effects[0].restrains_while_grappled is True
    assert attack.persistent_effects[1].condition_id == "blinded"


def test_failed_save_applies_multiple_effects_and_modifier_through_shared_pipeline() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"],
        monster_ids=["srd-commoner"],
    ))
    target = setup.heroes[0]
    actor = setup.monsters[0]
    base_speed = target.state.template.speed_ft
    action = SavingThrowAction(
        id="test-control-save",
        name="Control Burst",
        save_ability="strength",
        dc=30,
        range_ft=5,
        persistent_effects=[
            HitControlEffect(grapple_escape_dc=14, restrains_while_grappled=True),
            HitControlEffect(condition_id="blinded"),
        ],
        on_failure_modifier_effects=[
            HitModifierEffect(kind="speed", flat_bonus=-10, expires_at_end_of_target_turn=True),
        ],
    )

    event = resolve_save_action(
        1,
        1,
        actor,
        target,
        action,
        5,
        FixedDiceProvider([20]),
        affected_states=[actor.state, target.state],
    )

    assert event.save_succeeded is False
    assert {"grappled", "restrained", "blinded"} <= set(event.applied_condition_ids)
    assert target.state.grapple_sources[0].escape_dc == 14
    assert effective_speed(target.state) == base_speed - 10
