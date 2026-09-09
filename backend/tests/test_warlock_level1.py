from app.content.audited_warlock import build_varek_ashenmark_level
from app.content.audited_warlock_profile import build_varek_ashenmark_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_packages import build_class_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_varek_warlock_one_is_raw_ready_across_all_certification_layers() -> None:
    template = build_varek_ashenmark_level(1)
    profile = build_varek_ashenmark_profile()
    fingerprint = build_pregen_combat_profiles()[template.id]

    assert template.id == "varek-ashenmark-l1"
    assert template.name == "Varek Ashenmark"
    assert template.archetype == "Warlock"
    assert template.armor_class == 11
    assert template.max_hp == 8

    pact_blade = template.weapon_attack
    assert pact_blade.weapon.id == "longsword"
    assert pact_blade.attack_bonus == 5
    assert pact_blade.damage_bonus == 3
    assert pact_blade.attack_ability == "charisma"
    assert pact_blade.attack_ability_modifier == 3

    assert len(template.spell_attack_actions) == 1
    blast = template.spell_attack_actions[0]
    assert blast.id == "eldritch-blast"
    assert blast.level == 0
    assert blast.attack_bonus == 5
    assert blast.range_ft == 120
    assert blast.damage_dice_count == 1
    assert blast.damage_dice_size == 10
    assert blast.damage_type == "force"

    assert {item.id: item.max_uses for item in template.resources} == {
        "pact-slot-1": 1,
        "adrenaline-rush": 2,
        "relentless-endurance": 1,
    }

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, template)
    assert_pregen_combat_stats(template, fingerprint)
    assert_character_resources_raw_ready(template, profile, fingerprint)


def test_warlock_one_spell_package_and_engine_features_are_complete() -> None:
    package = build_class_spell_package("warlock", 1)
    assert [spell.id for spell in package.cantrips] == ["eldritch-blast", "prestidigitation"]
    assert [spell.id for spell in package.spells] == ["comprehend-languages", "detect-magic"]
    assert unsupported_hero_engine_features(canonical_combat_features("warlock", 1)) == ()
