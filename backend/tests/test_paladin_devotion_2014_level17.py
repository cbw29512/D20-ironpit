from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014


def test_level_17_is_incremental_fifth_level_spell_progression() -> None:
    level16 = build_aurelia_brightshield_2014(16)
    hero = build_aurelia_brightshield_2014(17)
    profile = build_aurelia_brightshield_2014_profile(17)
    combat_profile = build_aurelia_brightshield_2014_combat_profile(17)

    assert hero.level == 17
    assert hero.max_hp == level16.max_hp + 8 == 140
    assert hero.ability_scores == level16.ability_scores
    assert hero.passive_modifier_grants == level16.passive_modifier_grants

    resources = {item.id: item.max_uses for item in hero.resources}
    assert [resources[f"spell-slot-{level}"] for level in range(1, 6)] == [4, 3, 3, 3, 1]
    assert resources["lay-on-hands"] == 85
    assert resources["cleansing-touch"] == 4

    assert len(hero.spell_save_actions) == 1
    flame_strike = hero.spell_save_actions[0]
    assert flame_strike.id == "flame-strike"
    assert flame_strike.level == 5
    assert flame_strike.range_ft == 60
    assert flame_strike.area_radius_ft == 10
    assert flame_strike.save_ability == "dexterity"
    assert flame_strike.dc == 18
    assert flame_strike.success_damage == "half"
    assert [(item.dice_count, item.dice_size, item.damage_type) for item in flame_strike.damage_components] == [
        (4, 6, "fire"),
        (4, 6, "radiant"),
    ]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["flame-strike"].combat_relevant is True
    assert audits["flame-strike"].automated is True
    assert audits["commune"].combat_relevant is False
    assert audits["commune"].automated is False
    assert_character_resources_raw_ready(hero, profile, combat_profile)


def test_level_17_oath_spell_package_keeps_commune_noncombat_and_flame_strike_active() -> None:
    hero = build_aurelia_brightshield_2014(17)
    package = build_paladin_2014_spell_package(17, hero.ability_scores.modifier("charisma"))
    assert package is not None
    assert len(package.spells) == 12
    oath = {spell.id: spell for spell in package.always_prepared_spells}
    assert oath["commune"].required_capabilities == ["arena-out-of-scope"]
    assert oath["flame-strike"].required_capabilities == [
        "save-damage", "area-damage", "multi-component-damage",
    ]
