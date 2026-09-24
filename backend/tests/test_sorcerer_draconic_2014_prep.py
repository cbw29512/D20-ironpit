from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.sorcerer_draconic_2014_combat_profile import build_nyra_emberveil_2014_combat_profile
from app.content.sorcerer_draconic_2014_data import ability_scores
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_progression import sorcerer_draconic_2014_level
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014


def test_nyra_persistent_identity_and_draconic_math_are_stable_through_twenty() -> None:
    first = build_nyra_emberveil_2014_profile(1)
    for level in range(1, 21):
        profile = build_nyra_emberveil_2014_profile(level)
        runtime = build_nyra_emberveil_2014(level)
        fingerprint = build_nyra_emberveil_2014_combat_profile(level)
        assert profile.character_name == first.character_name == "Nyra Emberveil"
        assert profile.species_id == first.species_id == "human"
        assert profile.background_id == first.background_id == "hermit"
        assert profile.subclass_id == first.subclass_id == "draconic-bloodline"
        assert profile.template_id == runtime.id == fingerprint.template_id
        assert runtime.level == profile.level == fingerprint.level == level
        assert runtime.armor_class == fingerprint.armor_class == 13 + runtime.ability_scores.modifier("dexterity")
        assert runtime.max_hp == fingerprint.max_hp

    assert ability_scores(1).charisma == 16
    assert ability_scores(4).charisma == 18
    assert ability_scores(8).charisma == 20
    assert ability_scores(12).dexterity == 17
    assert ability_scores(16).dexterity == 19
    assert ability_scores(19).dexterity == 20


def test_nyra_resources_follow_2014_slots_and_sorcery_points() -> None:
    assert sorcerer_draconic_2014_level(1).sorcery_points == 0
    assert sorcerer_draconic_2014_level(2).sorcery_points == 2
    assert sorcerer_draconic_2014_level(20).sorcery_points == 20

    for level in (1, 2, 3, 6, 14, 18, 20):
        runtime = build_nyra_emberveil_2014(level)
        fingerprint = build_nyra_emberveil_2014_combat_profile(level)
        resources = {item.id: item.max_uses for item in runtime.resources}
        assert resources == dict(fingerprint.resources)
        if level == 1:
            assert "sorcery-points" not in resources
        else:
            assert resources["sorcery-points"] == level


def test_nyra_unfinished_outcome_changing_features_remain_blocked_and_uncertified() -> None:
    expected = {
        1: "sorcerer-spellcasting",
        2: "font-of-magic",
        3: "metamagic",
        6: "elemental-affinity",
        14: "dragon-wings",
        18: "draconic-presence",
    }
    for level, feature_id in expected.items():
        profile = build_nyra_emberveil_2014_profile(level)
        audit = next(item for item in profile.feature_audits if item.feature_id == feature_id)
        assert audit.automated is False

    assert all(
        not (
            item.class_id == "sorcerer"
            and getattr(item.template_builder, "__name__", "") == "build_nyra_emberveil_2014"
        )
        for item in CERTIFIED_HERO_PROGRESSIONS
    )
