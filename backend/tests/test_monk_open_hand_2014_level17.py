from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.deferred_save_effect import arm_deferred_save_effect, resolve_deferred_save_effect
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_entries_for_ruleset
from app.content.demo import build_demo_fighter
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _pair() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    monk_state = build_combatant_state(build_kael_stillwater_2014(17))
    target_template = build_demo_fighter().model_copy(update={
        "id": "quivering-palm-target",
        "name": "Quivering Palm Target",
        "max_hp": 100,
        "kind": "monster",
        "ruleset": "2014",
    })
    target_state = build_combatant_state(target_template)
    monk = EncounterCombatant(
        combatant_id="hero-1:kael-stillwater-2014-l17",
        side="heroes",
        position_ft=5,
        state=monk_state,
    )
    target = EncounterCombatant(
        combatant_id="monster-1:quivering-palm-target",
        side="monsters",
        position_ft=5,
        state=target_state,
    )
    setup = EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=17,
        monster_total_cr="0",
        ruleset="2014",
    )
    return monk, target, setup


def _ki(member: EncounterCombatant) -> int:
    return next(item for item in member.state.resources if item.id == "ki").current_uses


def test_level17_quivering_palm_is_exact_source_tagged_deferred_effect() -> None:
    hero = build_kael_stillwater_2014(17)
    rule = hero.progression_features.deferred_save_effect
    assert rule is not None
    assert rule.source_id == "quivering-palm"
    assert rule.source_name == "Quivering Palm"
    assert rule.trigger_attack_ids == ["unarmed-strike"]
    assert (rule.resource_id, rule.resource_cost) == ("ki", 3)
    assert (rule.save_ability, rule.save_dc) == ("constitution", 18)
    assert rule.failure_sets_zero_hp is True
    assert (rule.success_damage_dice_count, rule.success_damage_dice_size) == (10, 10)
    assert rule.success_damage_type == "necrotic"


def test_unarmed_hit_arms_one_target_spends_three_ki_and_logs_exact_name() -> None:
    monk, target, _ = _pair()
    event = resolve_attack(
        1, 1,
        monk.state,
        target.state,
        monk.state.template.weapon_attack,
        5,
        FixedDiceProvider([15, 4]),
        actor_event_id=monk.combatant_id,
        target_event_id=target.combatant_id,
        spend_action=False,
    )

    assert event.hit is True
    assert _ki(monk) == 14
    assert [(item.source_id, item.target_id) for item in monk.state.deferred_effects] == [
        ("quivering-palm", target.combatant_id),
    ]
    assert "Quivering Palm is armed." in event.description

    assert arm_deferred_save_effect(
        monk.state, "monster-2:other-target", "unarmed-strike",
    ) is None
    assert _ki(monk) == 14
    assert len(monk.state.deferred_effects) == 1


def test_quivering_palm_failed_save_reduces_true_hp_to_zero_and_spends_action() -> None:
    monk, target, setup = _pair()
    armed = arm_deferred_save_effect(monk.state, target.combatant_id, "unarmed-strike")
    assert armed == ("quivering-palm", "Quivering Palm")
    assert _ki(monk) == 14

    event = resolve_deferred_save_effect(
        2, 2, monk, setup, FixedDiceProvider([1]),
    )
    assert event is not None
    assert event.feature_id == "quivering-palm"
    assert event.save_succeeded is False
    assert target.state.current_hp == 0
    assert target.state.temporary_hp == 0
    assert target.state.is_dead is True
    assert monk.state.action_available is False
    assert monk.state.deferred_effects == []
    assert "Quivering Palm" in event.description


def test_quivering_palm_success_save_takes_ten_d10_necrotic_through_damage_rules() -> None:
    monk, target, setup = _pair()
    arm_deferred_save_effect(monk.state, target.combatant_id, "unarmed-strike")

    event = resolve_deferred_save_effect(
        2, 2, monk, setup,
        FixedDiceProvider([20, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]),
    )
    assert event is not None
    assert event.save_succeeded is True
    assert event.damage_roll is not None
    assert event.damage_roll.notation == "10d10"
    assert event.damage_roll.total == 50
    assert len(event.damage_components) == 1
    assert event.damage_components[0].source == "Quivering Palm"
    assert event.damage_components[0].damage_type.value == "necrotic"
    assert target.state.current_hp == 50
    assert monk.state.action_available is False
    assert monk.state.deferred_effects == []


def test_level17_profile_fingerprint_audit_and_registry_match() -> None:
    profile = build_kael_stillwater_2014_profile(17)
    fingerprint = build_kael_2014_combat_profile(17)
    registry = {
        key: (template.name, template.id)
        for key, template in build_certified_hero_entries_for_ruleset("2014")
    }

    quivering = next(item for item in profile.feature_audits if item.feature_id == "quivering-palm")
    assert quivering.combat_relevant is True
    assert quivering.automated is True
    assert fingerprint.level == 17
    assert fingerprint.abilities.wisdom == 19
    assert fingerprint.armor_class == 19
    assert registry[("monk", 17, "canonical-2014")] == (
        "Kael Stillwater",
        "kael-stillwater-2014-l17",
    )
