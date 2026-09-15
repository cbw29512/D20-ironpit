from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.modifier_stack import effective_speed
from app.combat.saving_throws import resolve_save_action
from app.content.capability_compiler import compile_combatant
from app.content.capability_from_template import definition_from_template
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.models import EncounterSelection, SavingThrowAction
from app.domain.save_effects import ConditionEffectDefinition, ProneEffectDefinition


def _setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    return setup, setup.monsters[0], setup.heroes[0]


def _action(dc: int = 30) -> SavingThrowAction:
    return SavingThrowAction(
        id="test-failed-save-riders",
        name="Test Failed Save Riders",
        save_ability="dexterity",
        dc=dc,
        range_ft=30,
        failure_effects=[
            ProneEffectDefinition(),
            ConditionEffectDefinition(
                condition="frightened", expiry_timing="target_turn_end",
            ),
            CombatModifierEffect(
                kind="speed", flat_bonus=-10, expires_at_end_of_target_turn=True,
            ),
        ],
    )


def test_failed_save_applies_ordered_condition_and_modifier_effects() -> None:
    setup, actor, target = _setup()
    event = resolve_save_action(
        1, 1, actor, target, _action(), 5, FixedDiceProvider([1]),
        affected_states=[actor.state, target.state],
    )
    assert event.save_succeeded is False
    assert event.applied_condition_ids == ["prone", "frightened"]
    assert target.state.active_effect_ids[-2:] == ["prone", "frightened"]
    assert target.state.timed_effects[0].source_effect_id == "test-failed-save-riders"
    assert effective_speed(target.state) == target.state.template.speed_ft - 10
    modifier = target.state.active_modifiers[0]
    assert modifier.id.endswith(":test-failed-save-riders:failed-save-modifier:2")
    assert modifier.expires_at_end_of_target_turn is True


def test_successful_save_applies_no_failure_effects() -> None:
    setup, actor, target = _setup()
    event = resolve_save_action(
        1, 1, actor, target, _action(dc=1), 5, FixedDiceProvider([20]),
        affected_states=[actor.state, target.state],
    )
    assert event.save_succeeded is True
    assert event.applied_condition_ids == []
    assert "prone" not in target.state.active_effect_ids
    assert "frightened" not in target.state.active_effect_ids
    assert target.state.active_modifiers == []


def test_failed_save_effects_survive_capability_round_trip() -> None:
    setup, actor, _ = _setup()
    template = actor.state.template.model_copy(update={"saving_throw_actions": [_action()]})
    definition = definition_from_template(template)
    rebuilt = compile_combatant(definition)
    action = rebuilt.saving_throw_actions[0]
    assert [effect.kind for effect in action.failure_effects] == [
        "prone", "condition", "speed",
    ]
    assert action.failure_effects[1].condition == "frightened"
    assert action.failure_effects[2].flat_bonus == -10
