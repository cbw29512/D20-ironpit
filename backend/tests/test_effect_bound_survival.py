"""Behavioral tests use compiled capability data without certifying blocked levels."""
import pytest
from unittest.mock import Mock

from app.combat.attacks import resolve_attack
from app.combat.barbarian import enter_rage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.undead_fortitude import consume_survival_save_log
from app.combat.zero_hp import apply_damage, restore_hit_points
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.demo import build_goblin_warrior
from app.content.hero_combat_feature_registry import compile_progression_feature_fields
from app.domain.progression import ProgressionCombatFeatures


def candidate(level=11):
    template = build_rokhan_stonefury_level(9).model_copy(update={
        "level": level, "max_hp": 115,
        "progression_features": ProgressionCombatFeatures(**compile_progression_feature_fields(
            ["relentless-rage"], level)),
    })
    state = build_combatant_state(template)
    enter_rage(1, 1, state, "candidate")
    state.current_hp = 1
    return state


def test_success_prevents_unconsciousness_and_does_not_spend_action_or_orc_resource():
    state = candidate()
    assert apply_damage(state, 1, dice=FixedDiceProvider([3])) == "survival_save"
    assert state.current_hp == 22  # 3 + certified Constitution save bonus 7 meets DC 10.
    assert not state.is_unconscious and "prone" not in state.active_effect_ids
    assert state.action_available and state.reaction_available
    assert next(r for r in state.resources if r.id == "relentless-endurance").current_uses == 1
    assert "DC 10" in consume_survival_save_log(state)
    assert consume_survival_save_log(state) == ""


def test_dc_escalates_after_success_and_failure_and_resets_only_with_fresh_state():
    state = candidate()
    apply_damage(state, 1, dice=FixedDiceProvider([3]))
    state.current_hp = 1
    assert apply_damage(state, 1, dice=FixedDiceProvider([1])) == "relentless_endurance"
    assert state.survival_save_uses == {"relentless-rage": 2}
    assert "DC 15" in consume_survival_save_log(state)
    assert apply_damage(state, 1, dice=FixedDiceProvider([13])) == "survival_save"
    assert state.current_hp == 22
    fresh = build_combatant_state(state.template)
    assert fresh.survival_save_uses == {} and fresh.pending_survival_save_logs == []
    assert state.template.progression_features.effect_bound_survival_save.initial_dc == 10


@pytest.mark.parametrize("kind", ["no-rage", "instant-death", "already-zero", "temp-hp"])
def test_nontriggers_never_roll_or_increase_dc(kind):
    state = candidate()
    amount = 1
    if kind == "no-rage":
        state.active_effect_ids.remove("rage")
    elif kind == "instant-death":
        amount = 116
    elif kind == "already-zero":
        state.current_hp = 0
    else:
        state.temporary_hp = 2
    apply_damage(state, amount, dice=Mock(roll=Mock(side_effect=AssertionError("unexpected roll"))))
    assert state.survival_save_uses == {}
    if kind == "instant-death":
        assert state.is_dead


def test_critical_and_radiant_do_not_exclude_this_save():
    from app.domain.models import DamageType
    state = candidate(20)
    assert apply_damage(state, 1, critical=True, damage_types={DamageType.RADIANT},
                        dice=FixedDiceProvider([3])) == "survival_save"
    assert state.current_hp == 40


def test_failure_falls_through_to_unconsciousness_when_orc_resource_is_spent():
    state = candidate()
    for resource in state.resources:
        resource.current_uses = 0
    assert apply_damage(state, 1, dice=FixedDiceProvider([1])) == "unconscious"
    restore_hit_points(state, 1)
    state.active_effect_ids.append("rage") if "rage" not in state.active_effect_ids else None
    assert apply_damage(state, 1, dice=FixedDiceProvider([8])) == "survival_save"
    assert "DC 15" in consume_survival_save_log(state)


def test_missing_dice_fails_closed():
    with pytest.raises(ValueError, match="requires a dice provider"):
        apply_damage(candidate(), 1)


def test_weapon_event_preserves_separate_survival_save_evidence():
    target = candidate()
    attacker = build_combatant_state(build_goblin_warrior())
    event = resolve_attack(2, 1, attacker, target, attacker.template.weapon_attack,
                           5, FixedDiceProvider([19, 4, 3]))
    assert target.current_hp == 22
    assert "relentless-rage: DC 10" in event.description
    assert "total 10" in event.description
    assert target.pending_survival_save_logs == []


def test_shared_save_modifiers_and_exported_data_are_used():
    from app.domain.modifiers import CombatModifier, ModifierKind
    from scripts.export_browser_heroes import _template
    state = candidate()
    state.active_modifiers.append(CombatModifier(id="save-boost", source_id="ally",
        source_effect_id="test-buff", kind=ModifierKind.SAVING_THROW_FLAT, flat_bonus=2))
    assert apply_damage(state, 1, dice=FixedDiceProvider([1])) == "survival_save"
    assert "modifier 9, total 10" in consume_survival_save_log(state)
    exported = _template(("barbarian", 11, "canonical"), state.template)
    assert exported["effect_bound_survival_save"] == {
        "source_id": "relentless-rage", "required_effect_id": "rage", "save_ability": "constitution",
        "initial_dc": 10, "dc_increment": 5, "replacement_hp": 22,
    }


def test_save_action_keeps_attack_save_and_survival_save_distinct():
    from app.combat.saving_throws import resolve_save_action
    from app.domain.actions import SavingThrowAction
    from app.domain.encounters import EncounterCombatant
    actor = EncounterCombatant(combatant_id="source", side="monsters", position_ft=5,
                                state=build_combatant_state(build_goblin_warrior()))
    target = EncounterCombatant(combatant_id="target", side="heroes", position_ft=0, state=candidate())
    action = SavingThrowAction(id="fire", name="Fire", save_ability="dexterity", dc=15,
        range_ft=30, damage_dice_count=1, damage_dice_size=6, damage_type="fire", success_damage="half")
    event = resolve_save_action(1, 1, actor, target, action, 5, FixedDiceProvider([1, 4, 3]))
    assert event.save_ability == "dexterity" and event.save_dc == 15 and not event.save_succeeded
    assert "relentless-rage: DC 10 constitution" in event.description
    assert event.hp_after == 22 and target.state.pending_survival_save_logs == []
