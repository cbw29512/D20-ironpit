from __future__ import annotations

from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.character_resource_rules import expected_resources
from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.content.ranger_hunter_2024_runtime import build_rowan_ashtrail_2024


def test_2024_ranger_level_one_is_conversion_of_rowan() -> None:
    profile = build_rowan_ashtrail_2024_profile(1)
    ranger = build_rowan_ashtrail_2024(1)

    assert profile.character_name == "Rowan Ashtrail"
    assert profile.ruleset == ranger.ruleset == "2024"
    assert profile.species_id == "wood-elf"
    assert profile.background_id == "outlander"
    assert profile.origin_feat_id == "alert"
    assert profile.weapon_masteries == ["longbow", "shortsword"]
    assert profile.final_ability_scores.dexterity == 17
    assert profile.final_ability_scores.wisdom == 15
    assert ranger.speed_ft == 35
    assert ranger.initiative_bonus == 5
    assert ranger.weapon_attack.weapon.id == "longbow"
    assert ranger.weapon_attack.weapon.mastery_property == "Slow"
    assert {item.weapon.id for item in ranger.alternate_weapon_attacks} == {"shortsword", "scimitar"}
    assert expected_resources(profile) == {
        "favored-enemy-hunters-mark": 2,
        "spell-slot-1": 2,
    }
    assert_canonical_profile_policy(profile)


def test_2024_ranger_hunters_mark_reuses_targeted_concentration_damage() -> None:
    ranger = build_rowan_ashtrail_2024(1)
    mark = ranger.targeted_concentration_damage_actions[0]

    assert mark.id == "hunters-mark"
    assert mark.damage_type == "force"
    assert (mark.dice_count, mark.dice_size) == (1, 6)
    assert mark.free_cast_resource_id == "favored-enemy-hunters-mark"
    assert mark.duration_rounds(1) == 600
    assert mark.duration_rounds(3) == 4800
    assert mark.duration_rounds(5) == 14400
