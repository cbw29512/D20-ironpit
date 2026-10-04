from __future__ import annotations

from app.content.ranger_hunter_2024_profile import build_rowan_ashtrail_2024_profile
from app.content.ranger_hunter_2024_runtime import build_rowan_ashtrail_2024


def test_2024_ranger_level_two_advances_same_rowan_with_archery_and_expertise() -> None:
    profile = build_rowan_ashtrail_2024_profile(2)
    hero = build_rowan_ashtrail_2024(2)

    assert profile.character_name == "Rowan Ashtrail"
    assert profile.level == hero.level == 2
    assert profile.fighting_styles == ["Archery"]
    assert hero.fighting_styles == ["Archery"]
    assert hero.max_hp == 18
    assert hero.initiative_bonus == 5
    assert hero.weapon_attack.weapon.id == "longbow"
    assert hero.weapon_attack.attack_bonus == 7
    assert hero.weapon_attack.damage_bonus == 3
    assert {item.weapon.id: item.attack_bonus for item in hero.alternate_weapon_attacks} == {
        "shortsword": 5,
        "scimitar": 5,
    }
    assert hero.skill_bonuses["perception"] == 6
    assert {item.id: item.max_uses for item in hero.resources} == {
        "favored-enemy-hunters-mark": 2,
        "spell-slot-1": 2,
    }


def test_2024_ranger_level_two_records_deft_explorer_archery_and_damage_first_spell() -> None:
    audits = {
        item.feature_id: item
        for item in build_rowan_ashtrail_2024_profile(2).feature_audits
    }

    assert audits["deft-explorer"].automated is True
    assert "Perception gains Expertise" in audits["deft-explorer"].notes
    assert audits["fighting-style"].automated is True
    assert "universal Archery" in audits["fighting-style"].notes
    assert audits["hail-of-thorns"].automated is False
    assert "fail-closed" in audits["hail-of-thorns"].notes
