from __future__ import annotations

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.certified_heroes import build_certified_hero_registry
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.sorcerer_draconic_2024_combat_profile import build_nyra_2024_combat_profile
from app.content.sorcerer_draconic_2024_profile import build_nyra_emberveil_2024_profile
from app.content.sorcerer_draconic_2024_runtime import build_nyra_emberveil_2024


def _validate(level: int):
    profile = build_nyra_emberveil_2024_profile(level)
    hero = build_nyra_emberveil_2024(level)
    fingerprint = build_nyra_2024_combat_profile(level)
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, fingerprint)
    assert_character_resources_raw_ready(hero, profile, fingerprint)
    return profile, hero


def test_2024_nyra_levels_one_through_twenty_pass_official_check() -> None:
    registry = build_certified_hero_registry()
    for level in range(1, 21):
        profile, hero = _validate(level)
        assert hero.name == "Nyra Emberveil"
        assert profile.character_name == "Nyra Emberveil"
        assert hero.ruleset == "2024"
        assert registry[("sorcerer", level, "canonical")] == (hero.name, hero.id)
        if level >= 3:
            assert any(item.id == "dragons-breath" for item in hero.spell_save_actions)
            assert any(item.id == "dragons-breath" for item in hero.timed_self_buff_actions)
            assert any(item.id == "dragons-breath-exhale" for item in hero.concentration_repeat_save_actions)
