from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.ranger_hunter_2014_combat_profile import build_rowan_ashtrail_2014_combat_profile
from app.content.ranger_hunter_2014_data import ability_scores
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_progression import ranger_hunter_2014_level
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_rowan_persistent_2014_identity_and_asi_progression() -> None:
    first = build_rowan_ashtrail_2014_profile(1)
    prior_advancements = 0
    for level in range(1, 21):
        profile = build_rowan_ashtrail_2014_profile(level)
        runtime = build_rowan_ashtrail_2014(level)
        fingerprint = build_rowan_ashtrail_2014_combat_profile(level)
        assert profile.character_name == first.character_name == "Rowan Ashtrail"
        assert profile.species_id == first.species_id == "human"
        assert profile.background_id == first.background_id == "outlander"
        assert profile.class_equipment == first.class_equipment
        assert profile.template_id == runtime.id == fingerprint.template_id
        assert profile.level == runtime.level == fingerprint.level == level
        assert len(profile.advancement_increases) >= prior_advancements
        prior_advancements = len(profile.advancement_increases)

    assert ability_scores(1).dexterity == 16
    assert ability_scores(4).dexterity == 18
    assert ability_scores(8).dexterity == 20
    assert ability_scores(12).wisdom == 17
    assert ability_scores(16).wisdom == 19
    assert ability_scores(19).wisdom == 20


def test_rowan_static_combat_math_resources_and_extra_attack_match_fingerprint() -> None:
    for level in (1, 2, 3, 5, 8, 11, 15, 20):
        runtime = build_rowan_ashtrail_2014(level)
        fingerprint = build_rowan_ashtrail_2014_combat_profile(level)
        row = ranger_hunter_2014_level(level)

        assert runtime.armor_class == fingerprint.armor_class == 16
        assert runtime.max_hp == fingerprint.max_hp
        assert runtime.initiative_bonus == fingerprint.initiative_bonus
        assert {item.id: item.max_uses for item in runtime.resources} == dict(fingerprint.resources)
        assert runtime.fighting_style == ("Archery" if level >= 2 else None)
        assert runtime.weapon_attack.attack_bonus == (
            row.proficiency_bonus + runtime.ability_scores.modifier("dexterity")
            + (2 if level >= 2 else 0)
        )
        assert (runtime.attack_action is not None) is (level >= 5)


def test_hunter_reuses_colossus_slayer_and_evasion_primitives() -> None:
    level_three = build_rowan_ashtrail_2014(3)
    rider = level_three.progression_features.once_per_turn_weapon_hit_damage_rider
    assert rider is not None
    assert rider.source_id == "colossus-slayer"
    assert rider.source_name == "Colossus Slayer"
    assert rider.dice_count == 1
    assert rider.dice_size == 8
    assert rider.requires_target_below_max_hp is True

    assert build_rowan_ashtrail_2014(14).progression_features.evasion is False
    assert build_rowan_ashtrail_2014(15).progression_features.evasion is True


def test_hunter_missing_mechanics_remain_explicitly_blocked_and_uncertified() -> None:
    expected = {
        2: "ranger-spellcasting",
        7: "multiattack-defense",
        8: "lands-stride",
        11: "volley",
        14: "vanish",
        18: "feral-senses",
        20: "foe-slayer",
    }
    for level, feature_id in expected.items():
        profile = build_rowan_ashtrail_2014_profile(level)
        audit = next(item for item in profile.feature_audits if item.feature_id == feature_id)
        assert audit.automated is False

    assert all(
        not (
            item.class_id == "ranger"
            and getattr(item.template_builder, "__name__", "") == "build_rowan_ashtrail_2014"
        )
        for item in CERTIFIED_HERO_PROGRESSIONS
    )
