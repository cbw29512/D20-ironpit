from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_registry
from app.content.ranger_hunter_2024_combat_profile import build_rowan_2024_combat_profile
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.content.ranger_hunter_2024_runtime import build_rowan_ashtrail_2024
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def _validate(level: int):
    profile = build_rowan_ashtrail_2024_profile(level)
    hero = build_rowan_ashtrail_2024(level)
    fingerprint = build_rowan_2024_combat_profile(level)
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, fingerprint)
    assert_character_resources_raw_ready(hero, profile, fingerprint)
    return profile, hero


def test_2024_rowan_levels_one_through_twenty_pass_official_check() -> None:
    registry = build_certified_hero_registry()
    for level in range(1, 21):
        profile, hero = _validate(level)
        assert hero.name == "Rowan Ashtrail"
        assert profile.character_name == "Rowan Ashtrail"
        assert profile.species_id == "wood-elf"
        assert profile.background_id == "outlander"
        assert profile.origin_feat_id == "alert"
        assert hero.ruleset == "2024"
        assert registry[("ranger", level, "canonical")] == (hero.name, hero.id)
        assert "hunters-mark" in {item.id for item in hero.targeted_concentration_damage_actions}
        assert "ensnaring-strike" in {item.id for item in hero.post_hit_save_condition_spells}
        if level >= 2:
            assert hero.fighting_style == "Archery"
            assert hero.skill_bonuses["perception"] == (
                profile.final_ability_scores.modifier("wisdom") + 2 * (2 + (level - 1) // 4)
            )
        if level >= 3:
            assert profile.subclass_id == "hunter"
            assert hero.progression_features.once_per_turn_weapon_hit_damage_rider is not None
        if level >= 6:
            assert hero.speed_ft == 45
            assert hero.movement_modes.climb_ft == 45
        if level >= 7:
            assert hero.progression_features.opportunity_attacks_against_disadvantage is True
        if level >= 9:
            assert any(item.id == "dispel-magic" for item in hero.effect_removal_actions)
        if level >= 10:
            assert any(item.id == "tireless" for item in hero.healing_actions)
        if level >= 11:
            assert hero.progression_features.hunters_mark_splash_range_ft == 30
        if level >= 13:
            assert "hunters-mark" in hero.progression_features.concentration_damage_immune_effect_ids
        if level >= 14:
            assert any(item.id == "natures-veil" for item in hero.timed_self_buff_actions)
        if level >= 15:
            assert hero.incoming_damage_type_resistance_reaction is not None
        if level >= 17:
            assert hero.progression_features.advantage_against_marked_effect_id == "hunters-mark"
        if level >= 18:
            assert hero.blindsight_ft == 30
        if level >= 19:
            assert any(item.id == "boon-combat-prowess" for item in hero.resources)
        if level == 20:
            mark = hero.targeted_concentration_damage_actions[0]
            assert mark.dice_size == 10
