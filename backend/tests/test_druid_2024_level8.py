from __future__ import annotations

from app.combat.effective_movement_modes import effective_movement_modes
from app.combat.spell_modifiers import apply_spell_modifiers
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.content.replacement_form_registry import replacement_form_source_template


def test_2024_druid_level_eight_progression_and_asi() -> None:
    profile = build_thalen_greenbough_profile(8)
    hero = build_thalen_greenbough_level(8)
    package = canonical_spell_package("druid", 8, "2024", 5)

    assert profile.level == 8
    assert hero.level == 8
    assert hero.max_hp == 43
    assert hero.ability_scores.wisdom == 20
    assert hero.ability_scores.charisma == 16
    assert hero.saving_throw_bonuses["wisdom"] == 8
    assert hero.skill_bonuses["nature"] == 9
    assert hero.skill_bonuses["survival"] == 8
    assert hero.skill_bonuses["insight"] == 8
    assert hero.skill_bonuses["perception"] == 8
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 2,
        "wild-shape": 3,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.spells) == 12
    assert package.spells[-1].id == "freedom-of-movement"

    combat = build_pregen_combat_profiles()[hero.id]
    assert_character_resources_raw_ready(hero, profile, combat)

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l8"].automated is True
    assert audits["wild-shape-improvement-l8"].automated is True


def test_2024_druid_level_eight_wild_shape_uses_certified_cr_one_brown_bear() -> None:
    hero = build_thalen_greenbough_level(8)
    action = hero.replacement_form_actions[0]

    assert action.form_template_id == "srd-brown-bear"
    assert action.action_cost == "bonus_action"
    assert action.hp_mode == "retain_owner"
    assert action.temporary_hp_on_enter == 8
    assert action.retain_creature_type is True
    assert action.replace_existing_form is True

    source = replacement_form_source_template("2024", action.form_template_id)
    assert source.challenge_rating == "1"
    assert source.ability_scores is not None
    assert source.ability_scores.model_dump() == {
        "strength": 17,
        "dexterity": 12,
        "constitution": 15,
        "intelligence": 2,
        "wisdom": 13,
        "charisma": 7,
    }

    active = compile_replacement_form_template(
        hero,
        source,
        retain_spellcasting=action.retain_spellcasting,
        retained_spell_action_ids=action.retained_spell_action_ids,
        retain_creature_type=action.retain_creature_type,
        retain_hit_points=action.hp_mode == "retain_owner",
    )
    assert active.id.endswith("--form-srd-brown-bear")
    assert active.max_hp == hero.max_hp
    assert active.creature_type == "Humanoid"
    assert active.ability_scores is not None
    assert active.ability_scores.strength == 17
    assert active.ability_scores.dexterity == 12
    assert active.ability_scores.constitution == 15
    assert active.ability_scores.intelligence == hero.ability_scores.intelligence
    assert active.ability_scores.wisdom == hero.ability_scores.wisdom
    assert active.ability_scores.charisma == hero.ability_scores.charisma


def test_2024_druid_level_eight_freedom_of_movement_reuses_debuff_counters() -> None:
    hero = build_thalen_greenbough_level(8)
    spell = next(item for item in hero.defensive_spell_actions if item.id == "freedom-of-movement")

    assert (
        spell.level,
        spell.action_cost,
        spell.range_ft,
        spell.duration_minutes,
        spell.target_policy,
        spell.target_count,
        spell.target_count_per_slot_above,
        spell.concentration,
    ) == (4, "action", 5, 60, "friendly", 1, 1, False)

    signatures = {
        (
            item.debuff_counter.debuff_id,
            item.debuff_counter.source_scope,
            item.debuff_counter.mode,
            item.debuff_counter.movement_cost_ft,
        )
        for item in spell.modifier_effects
        if item.debuff_counter is not None
    }
    assert len(spell.movement_mode_grants) == 1
    swim = spell.movement_mode_grants[0]
    assert (swim.mode, swim.fixed_speed_ft, swim.match_current_speed) == ("swim", None, True)

    state = build_combatant_state(hero)
    apply_spell_modifiers(state, [("thalen", state)], "thalen", spell, 0)
    assert effective_movement_modes(state).swim_ft == hero.speed_ft

    assert signatures == {
        ("difficult-terrain", "any", "prevent", 0),
        ("speed-reduction", "magical", "prevent", 0),
        ("paralyzed", "magical", "prevent", 0),
        ("restrained", "magical", "prevent", 0),
        ("grappled", "nonmagical", "remove-with-movement", 5),
        ("restrained", "nonmagical", "remove-with-movement", 5),
    }
