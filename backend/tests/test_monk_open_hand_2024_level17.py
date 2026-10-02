from __future__ import annotations

from app.combat.deferred_save_effect import arm_deferred_save_effect
from app.combat.deferred_save_effect_attack_slot import resolve_deferred_effect_attack_slot
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterCombatant, EncounterSetup]:
    monk = EncounterCombatant(
        combatant_id="hero-1:kael-l17",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_kael_stillwater_2024(17)),
    )
    base = build_karnok_stoneward_level(1).model_copy(update={"max_hp": 300})
    first = EncounterCombatant(
        combatant_id="monster-1:first",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(base),
    )
    second = EncounterCombatant(
        combatant_id="monster-2:second",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(base),
    )
    setup = EncounterSetup(
        heroes=[monk],
        monsters=[first, second],
        hero_total_levels=17,
        monster_total_cr="0",
        ruleset="2024",
    )
    return monk, first, second, setup


def test_2024_open_hand_monk_level17_advances_pb_die_focus_and_derived_stats() -> None:
    level16 = build_kael_stillwater_2024(16)
    template = build_kael_stillwater_2024(17)
    profile = build_kael_stillwater_2024_profile(17)
    fingerprint = build_kael_2024_combat_profiles(17)[-1]

    assert template.level == profile.level == fingerprint.level == 17
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (17, 139, 55, 11)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (17, 139, 55, 11)
    assert level16.weapon_attack.weapon.dice_size == 10
    assert template.weapon_attack.weapon.dice_size == 12
    assert template.weapon_attack.attack_bonus == 11
    assert template.weapon_attack.damage_bonus == 5
    assert template.saving_throw_bonuses == {
        "strength": 7,
        "dexterity": 11,
        "constitution": 9,
        "intelligence": 6,
        "wisdom": 8,
        "charisma": 6,
    }
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 17
    assert template.healing_actions[0].dice_size == 12
    assert template.progression_features.resource_backed_on_hit_save_rider.save_dc == 16
    assert template.attack_damage_reduction_reaction.zero_damage_redirect.save_dc == 16
    assert template.attack_damage_reduction_reaction.zero_damage_redirect.damage_dice_size == 12


def test_2024_quivering_palm_binds_universal_deferred_effect_parameters() -> None:
    template = build_kael_stillwater_2024(17)
    rule = template.progression_features.deferred_save_effect

    assert rule is not None
    assert rule.source_id == "quivering-palm"
    assert rule.source_name == "Quivering Palm"
    assert rule.trigger_weapon_ids == ["unarmed-strike"]
    assert (rule.resource_id, rule.resource_cost) == ("focus-points", 4)
    assert (rule.save_ability, rule.save_dc) == ("constitution", 16)
    assert (rule.failure_damage_dice_count, rule.failure_damage_dice_size) == (10, 12)
    assert rule.failure_damage_type == "force"
    assert rule.success_damage_from_failure == "half"
    assert rule.failure_sets_zero_hp is False
    assert rule.allow_attack_slot_activation is True
    assert rule.allow_harmless_end_on_rearm is True
    assert rule.max_active_targets == 1


def test_2024_quivering_palm_attack_slot_deals_full_or_half_force_damage() -> None:
    monk, first, _, setup = _setup()
    rule = monk.state.template.progression_features.deferred_save_effect
    assert rule is not None

    armed = arm_deferred_save_effect(
        monk.state, first.state, first.combatant_id,
        monk.state.template.weapon_attack, 1,
    )
    assert armed is not None
    assert armed.resource_remaining == 13
    monk.state.action_available = False
    failed = resolve_deferred_effect_attack_slot(
        1, 1, monk, setup, FixedDiceProvider([1, *([12] * 10)]),
    )
    assert failed is not None
    assert failed.save_succeeded is False
    assert failed.damage_roll is not None and failed.damage_roll.total == 120
    assert first.state.current_hp == 180
    assert monk.state.action_available is False
    assert monk.state.deferred_effects == []

    first.state.current_hp = 300
    armed = arm_deferred_save_effect(
        monk.state, first.state, first.combatant_id,
        monk.state.template.weapon_attack, 2,
    )
    assert armed is not None
    succeeded = resolve_deferred_effect_attack_slot(
        2, 2, monk, setup, FixedDiceProvider([20, *([12] * 10)]),
    )
    assert succeeded is not None
    assert succeeded.save_succeeded is True
    assert succeeded.damage_roll is not None and succeeded.damage_roll.total == 60
    assert first.state.current_hp == 240
    assert monk.state.deferred_effects == []


def test_quivering_palm_harmless_rearm_replaces_old_target_but_not_same_target() -> None:
    monk, first, second, _ = _setup()

    first_arm = arm_deferred_save_effect(
        monk.state, first.state, first.combatant_id,
        monk.state.template.weapon_attack, 1,
    )
    assert first_arm is not None and first_arm.resource_remaining == 13

    duplicate = arm_deferred_save_effect(
        monk.state, first.state, first.combatant_id,
        monk.state.template.weapon_attack, 1,
    )
    assert duplicate is None
    assert next(item for item in monk.state.resources if item.id == "focus-points").current_uses == 13

    replacement = arm_deferred_save_effect(
        monk.state, second.state, second.combatant_id,
        monk.state.template.weapon_attack, 1,
    )
    assert replacement is not None and replacement.resource_remaining == 9
    assert [(item.source_id, item.target_id) for item in monk.state.deferred_effects] == [
        ("quivering-palm", second.combatant_id),
    ]


def test_2024_open_hand_monk_level17_audit_and_registry_are_certified() -> None:
    profile = build_kael_stillwater_2024_profile(17)
    audits = {item.feature_id: item for item in profile.feature_audits}
    palm = audits["quivering-palm"]

    assert palm.combat_relevant is True
    assert palm.automated is True
    assert "10d12 Force" in (palm.notes or "")
    assert build_kael_stillwater_2024(16).progression_features.deferred_save_effect is None

    registry = build_certified_hero_registry()
    assert registry[("monk", 17, "canonical")] == ("Kael Stillwater", "kael-stillwater-l17")
