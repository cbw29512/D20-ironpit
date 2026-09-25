from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014


def test_level_18_is_incremental_aura_expansion_progression() -> None:
    level17 = build_aurelia_brightshield_2014(17)
    hero = build_aurelia_brightshield_2014(18)
    profile = build_aurelia_brightshield_2014_profile(18)
    combat_profile = build_aurelia_brightshield_2014_combat_profile(18)

    assert hero.level == 18
    assert hero.max_hp == level17.max_hp + 8 == 148
    assert hero.ability_scores == level17.ability_scores
    assert hero.passive_modifier_grants == level17.passive_modifier_grants
    assert hero.spell_save_actions == level17.spell_save_actions

    resources = {item.id: item.max_uses for item in hero.resources}
    assert [resources[f"spell-slot-{level}"] for level in range(1, 6)] == [4, 3, 3, 3, 1]
    assert resources["lay-on-hands"] == 90
    assert resources["cleansing-touch"] == 4

    features17 = level17.progression_features
    features18 = hero.progression_features
    assert features17.aura_radius_2014_ft == 10
    assert features18.aura_radius_2014_ft == 30
    assert features18.aura_of_protection_2014_bonus == features17.aura_of_protection_2014_bonus == 4
    assert features18.aura_of_devotion_2014 is True
    assert features18.aura_of_courage_2014 is True

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["aura-improvements"].combat_relevant is True
    assert audits["aura-improvements"].automated is True

    assert_character_resources_raw_ready(hero, profile, combat_profile)
