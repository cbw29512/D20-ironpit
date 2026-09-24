from app.content.build_audit import audit_character_build
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_aurelia_level12_canonical_asi_and_derived_stats() -> None:
    profile = build_aurelia_brightshield_2014_profile(12)
    runtime = build_aurelia_brightshield_2014(12)
    fingerprint = build_aurelia_brightshield_2014_combat_profile(12)

    assert profile.final_ability_scores.strength == 20
    assert profile.final_ability_scores.charisma == 17
    assert runtime.ability_scores.strength == 20
    assert runtime.max_hp == 100
    assert runtime.progression_features.aura_of_protection_2014_bonus == 3
    assert next(resource for resource in runtime.resources if resource.id == "lay-on-hands").max_uses == 60
    assert [(resource.id, resource.max_uses) for resource in runtime.resources if resource.id.startswith("spell-slot-")] == [
        ("spell-slot-1", 4),
        ("spell-slot-2", 3),
        ("spell-slot-3", 3),
    ]

    assert_pregen_combat_stats(runtime, fingerprint)
    assert_character_resources_raw_ready(runtime, profile, fingerprint)
    assert audit_character_build(profile, runtime) == []


def test_aurelia_level12_reuses_existing_combat_capabilities() -> None:
    runtime = build_aurelia_brightshield_2014(12)

    assert len(runtime.attack_action.slots) == 2
    assert runtime.progression_features.divine_smite_2014 is True
    assert runtime.progression_features.aura_of_devotion_2014 is True
    assert runtime.progression_features.aura_of_courage_2014 is True
    assert runtime.weapon_attack.on_hit_damage[0].source == "Improved Divine Smite"
    assert runtime.weapon_attack.on_hit_damage[0].dice_count == 1
    assert runtime.weapon_attack.on_hit_damage[0].dice_size == 8


def test_aurelia_level12_prepared_spell_capacity_is_explicitly_covered() -> None:
    profile = build_aurelia_brightshield_2014_profile(12)
    charisma_modifier = profile.final_ability_scores.modifier("charisma")
    package = build_paladin_2014_spell_package(12, charisma_modifier)
    prepared = [spell for spell in package.spells if spell.prepared]

    assert len(prepared) == 9
    magic_weapon = next(spell for spell in prepared if spell.id == "magic-weapon")
    assert set(magic_weapon.capability_ids) == {"modifier-stack", "concentration"}
