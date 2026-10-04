from __future__ import annotations

from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.certified_heroes import build_certified_hero_registry
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.wizard_evoker_2024_combat_profile import build_elian_2024_combat_profile
from app.content.wizard_evoker_2024_profile import build_elian_starweaver_2024_profile
from app.content.wizard_evoker_2024_runtime import build_elian_starweaver_2024


def _validate(level: int):
    profile = build_elian_starweaver_2024_profile(level)
    hero = build_elian_starweaver_2024(level)
    fingerprint = build_elian_2024_combat_profile(level)
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, fingerprint)
    assert_character_resources_raw_ready(hero, profile, fingerprint)
    return profile, hero


def test_2024_elian_levels_one_through_twenty_pass_official_check() -> None:
    registry = build_certified_hero_registry()
    for level in range(1, 21):
        profile, hero = _validate(level)
        assert hero.name == "Elian Starweaver"
        assert hero.max_hp == 6 + 4 * (level - 1)
        assert hero.armor_class == 10
        assert hero.starts_with_heroic_inspiration is True
        assert registry[("wizard", level, "canonical")] == (hero.name, hero.id)
        if level >= 3:
            fire_bolt = next(item for item in hero.spell_attack_actions if item.id == "fire-bolt")
            poison = next(item for item in hero.spell_attack_actions if item.id == "poison-spray")
            thunderclap = next(item for item in hero.spell_save_actions if item.id == "thunderclap")
            assert fire_bolt.miss_damage == "half"
            assert poison.miss_damage == "half"
            assert thunderclap.success_damage == "half"
            assert profile.subclass_id == "evoker"
        if level >= 6:
            assert hero.progression_features.area_spell_ally_protection is not None
        if level >= 10:
            fire_bolt = next(item for item in hero.spell_attack_actions if item.id == "fire-bolt")
            assert fire_bolt.damage_bonus == hero.ability_scores.modifier("intelligence")
        if level >= 14:
            assert hero.progression_features.spell_damage_maximizer is not None
        if level >= 18:
            ids = {item.spell_id for item in hero.progression_features.alternate_spell_cast_grants}
            assert {"burning-hands", "shatter"}.issubset(ids)
        if level >= 19:
            assert profile.final_ability_scores.intelligence == 20
            assert any(item.id == "boon-of-fate" for item in hero.resources)
        if level == 20:
            resources = {item.id: item.max_uses for item in hero.resources}
            assert resources["signature-spell-fireball"] == 1
            assert resources["signature-spell-lightning-bolt"] == 1
            assert resources["spell-slot-9"] == 1
