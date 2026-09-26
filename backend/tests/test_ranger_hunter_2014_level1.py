from __future__ import annotations

from app.content.ranger_2014_progression import ranger_2014_level
from app.content.ranger_hunter_2014_profile import build_rowan_ashtrail_2014_profile
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014


def test_2014_ranger_level_one_is_legal_archer_baseline() -> None:
    hero = build_rowan_ashtrail_2014(1)
    profile = build_rowan_ashtrail_2014_profile(1)
    row = ranger_2014_level(1)

    assert hero.id == "rowan-ashtrail-2014-l1"
    assert hero.name == "Rowan Ashtrail"
    assert hero.ruleset == "2014"
    assert hero.level == 1
    assert hero.max_hp == 12
    assert hero.armor_class == 14
    assert hero.speed_ft == 35
    assert hero.ability_scores.dexterity == 17
    assert hero.ability_scores.wisdom == 14
    assert hero.weapon_attack.weapon.id == "longbow"
    assert hero.weapon_attack.attack_bonus == 5
    assert hero.weapon_attack.damage_bonus == 3
    assert hero.alternate_weapon_attacks[0].weapon.id == "shortsword"
    assert hero.saving_throw_bonuses["strength"] == 3
    assert hero.saving_throw_bonuses["dexterity"] == 5
    assert hero.skill_bonuses["stealth"] == 5
    assert hero.skill_bonuses["perception"] == 4
    assert profile.subclass_id is None
    assert profile.combat_loadout_kind == "dual-wield"
    assert row.spells_known == 0
    assert row.spell_slots == (0, 0, 0, 0, 0)
    grants = hero.progression_features.saving_throw_advantage_grants
    assert len(grants) == 1
    assert grants[0].source_id == "fey-ancestry"
    assert grants[0].required_effect_tags == ["charm"]


def test_2014_ranger_level_one_features_are_arena_neutral() -> None:
    profile = build_rowan_ashtrail_2014_profile(1)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["favored-enemy"].combat_relevant is False
    assert audits["natural-explorer"].combat_relevant is False
    assert all(item.automated for item in audits.values())
