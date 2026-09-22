from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.deferred_save_effect import (
    cleanup_deferred_effects,
    deferred_save_effect_candidate,
    resolve_deferred_save_effect,
)
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


def _setup(*, necrotic_resistance: bool = False) -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    monk = EncounterCombatant(
        combatant_id="hero-1:kael-l17",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_kael_stillwater_2014(17)),
    )
    target_template = build_aurelia_brightshield_2014(1).model_copy(
        update={
            "max_hp": 200,
            "damage_resistances": [DamageType.NECROTIC] if necrotic_resistance else [],
        }
    )
    target = EncounterCombatant(
        combatant_id="monster-1:target",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(target_template),
    )
    setup = EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=17,
        monster_total_cr="0",
        ruleset="2014",
    )
    return monk, target, setup


def _arm(monk: EncounterCombatant, target: EncounterCombatant, setup: EncounterSetup) -> None:
    begin_turn(monk.state)
    event = resolve_attack(
        1,
        1,
        monk.state,
        target.state,
        monk.state.template.weapon_attack,
        5,
        FixedDiceProvider([15, 4]),
        actor_event_id=monk.combatant_id,
        target_event_id=target.combatant_id,
        spend_action=True,
        turn_key="1:hero-1:kael-l17",
        affected_states=[monk.state, target.state],
    )
    assert event.hit is True
    assert "Quivering Palm is armed" in event.description
    assert event.resource_remaining == 14


def test_level17_snapshot_binds_quivering_palm_to_universal_deferred_effect() -> None:
    hero = build_kael_stillwater_2014(17)
    profile = build_kael_stillwater_2014_profile(17)
    fingerprint = build_kael_2014_combat_profile(17)
    rule = hero.progression_features.deferred_save_effect

    assert rule is not None
    assert rule.source_id == "quivering-palm"
    assert rule.source_name == "Quivering Palm"
    assert rule.trigger_weapon_ids == ["unarmed-strike"]
    assert rule.resource_id == "ki"
    assert rule.resource_cost == 3
    assert rule.save_ability == "constitution"
    assert rule.save_dc == 18
    assert rule.failure_sets_zero_hp is True
    assert (rule.success_damage_dice_count, rule.success_damage_dice_size) == (10, 10)
    assert rule.success_damage_type == "necrotic"
    assert rule.max_active_targets == 1
    assert hero.weapon_attack.weapon.dice_size == 10
    assert next(item for item in hero.resources if item.id == "ki").max_uses == 17
    assert fingerprint.attacks[0].dice_size == 10

    audit = next(item for item in profile.feature_audits if item.feature_id == "quivering-palm")
    assert audit.combat_relevant is True
    assert audit.automated is True


def test_unarmed_hit_spends_three_ki_and_arms_only_one_target() -> None:
    monk, target, setup = _setup()
    _arm(monk, target, setup)

    assert monk.state.action_available is False
    assert next(item for item in monk.state.resources if item.id == "ki").current_uses == 14
    assert [(item.source_id, item.target_id, item.armed_round) for item in monk.state.deferred_effects] == [
        ("quivering-palm", target.combatant_id, 1),
    ]
    assert deferred_save_effect_candidate(monk, setup) is None

    second = resolve_attack(
        2,
        1,
        monk.state,
        target.state,
        monk.state.template.weapon_attack,
        5,
        FixedDiceProvider([15, 4]),
        actor_event_id=monk.combatant_id,
        target_event_id=target.combatant_id,
        spend_action=False,
        turn_key="1:bonus",
        affected_states=[monk.state, target.state],
    )
    assert second.hit is True
    assert "Quivering Palm is armed" not in second.description
    assert next(item for item in monk.state.resources if item.id == "ki").current_uses == 14
    assert len(monk.state.deferred_effects) == 1


def test_failed_quivering_palm_save_reduces_true_hp_to_zero_on_next_turn() -> None:
    monk, target, setup = _setup()
    _arm(monk, target, setup)
    begin_turn(monk.state)

    assert deferred_save_effect_candidate(monk, setup) is target
    event = resolve_deferred_save_effect(
        2,
        2,
        monk,
        setup,
        FixedDiceProvider([1]),
    )

    assert event is not None
    assert event.feature_id == "quivering-palm"
    assert "Quivering Palm" in event.description
    assert event.save_succeeded is False
    assert target.state.current_hp == 0
    assert target.state.is_unconscious is True
    assert target.state.is_dead is False
    assert monk.state.action_available is False
    assert monk.state.deferred_effects == []


def test_successful_quivering_palm_save_deals_typed_damage_through_defenses() -> None:
    monk, target, setup = _setup(necrotic_resistance=True)
    _arm(monk, target, setup)
    hp_before = target.state.current_hp
    begin_turn(monk.state)

    event = resolve_deferred_save_effect(
        2,
        2,
        monk,
        setup,
        FixedDiceProvider([20, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
    )

    assert event is not None
    assert event.save_succeeded is True
    assert event.damage_roll is not None
    assert event.damage_roll.total == 5
    assert len(event.damage_components) == 1
    assert event.damage_components[0].source == "Quivering Palm"
    assert event.damage_components[0].total == 10
    assert event.damage_components[0].applied_total == 5
    assert target.state.current_hp == hp_before - 5
    assert monk.state.deferred_effects == []


def test_deferred_candidate_discovery_is_read_only_and_lifecycle_cleanup_prunes_stale_marks() -> None:
    monk, target, setup = _setup()
    _arm(monk, target, setup)
    begin_turn(monk.state)

    before = list(monk.state.deferred_effects)
    assert deferred_save_effect_candidate(monk, setup) is target
    assert monk.state.deferred_effects == before

    target.state.current_hp = 0
    target.state.is_unconscious = True
    assert deferred_save_effect_candidate(monk, setup) is None
    assert monk.state.deferred_effects == before

    cleanup_deferred_effects(setup)
    assert monk.state.deferred_effects == []
