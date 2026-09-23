from __future__ import annotations

from app.combat.deferred_save_effect import arm_deferred_save_effect, resolve_deferred_save_effect
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_entries_for_ruleset
from app.content.demo import build_goblin_warrior
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profile
from app.content.monk_open_hand_2014_profile import build_kael_stillwater_2014_profile
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup(*, target_con_save: int | None = None) -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero = EncounterCombatant(
        combatant_id="hero-1:kael-stillwater-2014-l17",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_kael_stillwater_2014(17)),
    )
    target_template = build_goblin_warrior().model_copy(deep=True)
    target_template.max_hp = 100
    if target_con_save is not None:
        target_template.saving_throw_bonuses = {
            **target_template.saving_throw_bonuses,
            "constitution": target_con_save,
        }
    target = EncounterCombatant(
        combatant_id="monster-1:test-goblin",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(target_template),
    )
    return hero, target, EncounterSetup(
        heroes=[hero], monsters=[target], hero_total_levels=17, monster_total_cr="0",
    )


def test_level17_quivering_palm_is_declared_through_generic_deferred_effect() -> None:
    hero = build_kael_stillwater_2014(17)
    rule = hero.progression_features.deferred_save_effect
    assert rule is not None
    assert rule.source_id == "quivering-palm"
    assert rule.source_name == "Quivering Palm"
    assert rule.trigger_attack_ids == ["unarmed-strike"]
    assert (rule.resource_id, rule.resource_cost) == ("ki", 3)
    assert (rule.save_ability, rule.save_dc) == ("constitution", 18)
    assert rule.failure_sets_zero_hp is True
    assert (
        rule.success_damage_dice_count,
        rule.success_damage_dice_size,
        rule.success_damage_type,
    ) == (10, 10, "necrotic")
    assert hero.weapon_attack.weapon.dice_size == 10
    assert next(item for item in hero.resources if item.id == "ki").max_uses == 17


def test_shared_attack_hit_arms_quivering_palm_and_spends_three_ki() -> None:
    hero, target, setup = _setup()
    event = resolve_encounter_attack(
        1,
        1,
        hero,
        target,
        hero.state.template.weapon_attack,
        5,
        FixedDiceProvider([20, 1, 1]),
        setup,
        spend_action=False,
    )
    assert event.hit is True
    assert "Quivering Palm is armed" in event.description
    assert next(item for item in hero.state.resources if item.id == "ki").current_uses == 14
    assert [(item.source_id, item.target_id) for item in hero.state.deferred_effects] == [
        ("quivering-palm", target.combatant_id),
    ]


def test_quivering_palm_failed_save_uses_shared_zero_hp_lifecycle() -> None:
    hero, target, setup = _setup()
    assert arm_deferred_save_effect(hero.state, target.combatant_id, "unarmed-strike") == "Quivering Palm"
    event = resolve_deferred_save_effect(1, 2, hero, setup, FixedDiceProvider([1]))
    assert event is not None
    assert event.feature_id == "quivering-palm"
    assert event.save_succeeded is False
    assert event.damage_roll is None
    assert target.state.current_hp == 0
    assert target.state.is_dead is True
    assert hero.state.action_available is False
    assert hero.state.deferred_effects == []
    assert "activates Quivering Palm" in event.description


def test_quivering_palm_success_deals_10d10_necrotic_through_damage_pipeline() -> None:
    hero, target, setup = _setup(target_con_save=30)
    assert arm_deferred_save_effect(hero.state, target.combatant_id, "unarmed-strike") == "Quivering Palm"
    event = resolve_deferred_save_effect(
        1, 2, hero, setup, FixedDiceProvider([1, *([1] * 10)]),
    )
    assert event is not None
    assert event.save_succeeded is True
    assert event.damage_roll is not None
    assert event.damage_roll.notation == "10d10"
    assert event.damage_roll.total == 10
    assert target.state.current_hp == 90
    assert event.damage_components[0].damage_type.value == "necrotic"
    assert hero.state.deferred_effects == []


def test_level17_profile_fingerprint_audit_and_registry_match() -> None:
    profile = build_kael_stillwater_2014_profile(17)
    fingerprint = build_kael_2014_combat_profile(17)
    registry = {
        key: (template.name, template.id)
        for key, template in build_certified_hero_entries_for_ruleset("2014")
    }
    audit = next(item for item in profile.feature_audits if item.feature_id == "quivering-palm")
    assert audit.combat_relevant is True
    assert audit.automated is True
    assert fingerprint.attacks[0].dice_size == 10
    assert fingerprint.resources == (("ki", 17), ("wholeness-of-body", 1))
    assert registry[("monk", 17, "canonical-2014")] == (
        "Kael Stillwater", "kael-stillwater-2014-l17",
    )
