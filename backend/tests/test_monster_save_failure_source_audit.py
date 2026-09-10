from app.content.monster_attack_source_audit import save_action_issues
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.models import SavingThrowAction
from app.domain.save_effects import (
    ConditionEffectDefinition,
    GrappleEffectDefinition,
    ProneEffectDefinition,
)
from app.domain.size import CreatureSize


def test_failed_save_effects_match_explicit_source_text() -> None:
    action = SavingThrowAction(
        id="test-pulse", name="Test Pulse", save_ability="dexterity", dc=14, range_ft=30,
        failure_effects=[
            ProneEffectDefinition(max_target_size=CreatureSize.LARGE),
            ConditionEffectDefinition(
                condition="frightened", expiry_timing="target_turn_end",
            ),
            CombatModifierEffect(kind="speed", flat_bonus=-10, expires_at_end_of_target_turn=True),
            CombatModifierEffect(kind="attacks-against-advantage"),
        ],
    )
    source = (
        "test pulse. dexterity saving throw: dc 14. failure: a large or smaller target has the prone condition "
        "and the frightened condition until the end of its next turn. its speed is reduced by 10 feet. "
        "attack rolls against it have advantage."
    )
    assert save_action_issues(action, source) == []


def test_failed_save_grapple_requires_source_escape_dc_and_restrained_text() -> None:
    action = SavingThrowAction(
        id="test-constrict", name="Test Constrict", save_ability="strength", dc=13, range_ft=10,
        failure_effects=[GrappleEffectDefinition(
            escape_dc=15, max_target_size=CreatureSize.MEDIUM, restrains=True,
        )],
    )
    good = (
        "test constrict. strength saving throw: dc 13. failure: the medium or smaller target has the grappled "
        "condition (escape dc 15) and is restrained while grappled."
    )
    bad = good.replace("escape dc 15", "escape dc 14")
    assert save_action_issues(action, good) == []
    assert "save-failure-effect-mismatch:test-constrict:0:grapple" in save_action_issues(action, bad)


def test_repeat_save_and_modifier_drift_fail_closed() -> None:
    action = SavingThrowAction(
        id="test-fear", name="Test Fear", save_ability="wisdom", dc=12, range_ft=30,
        failure_effects=[
            ConditionEffectDefinition(
                condition="frightened", repeat_save_ability="wisdom", repeat_save_dc=12,
                repeat_save_timing="target_turn_end",
            ),
            CombatModifierEffect(kind="speed", flat_bonus=-15),
        ],
    )
    source = (
        "test fear. wisdom saving throw: dc 12. failure: the target has the frightened condition. "
        "it repeats the saving throw at the end of each of its turns. its speed is reduced by 10 feet."
    )
    issues = save_action_issues(action, source)
    assert "save-failure-effect-mismatch:test-fear:0:condition" not in issues
    assert "save-failure-effect-mismatch:test-fear:1:speed" in issues
