from app.content.audited_cleric import build_seraphine_dawnshield
from app.content.audited_cleric_profile import build_seraphine_dawnshield_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.offensive_spell_effects import build_sacred_flame
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_seraphine_level_one_package_is_raw_audited() -> None:
    template = build_seraphine_dawnshield()
    profile = build_seraphine_dawnshield_profile()
    combat = build_pregen_combat_profiles()[template.id]
    spells = canonical_spell_package("cleric", 1)

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, template)
    assert_pregen_combat_stats(template, combat)
    assert_character_resources_raw_ready(template, profile, combat)

    assert template.armor_class == 17
    assert template.max_hp == 10
    assert template.saving_throw_bonuses["wisdom"] == 5
    assert template.saving_throw_bonuses["charisma"] == 2
    assert {item.id: item.max_uses for item in template.resources} == {
        "spell-slot-1": 2,
        "adrenaline-rush": 2,
        "relentless-endurance": 1,
    }
    assert [spell.id for spell in spells.cantrips] == ["sacred-flame", "light", "thaumaturgy"]
    assert [spell.id for spell in spells.spells] == ["bless", "cure-wounds", "guiding-bolt", "shield-of-faith"]
    assert [spell.id for spell in template.spell_save_actions] == ["sacred-flame"]
    assert [spell.id for spell in template.spell_attack_actions] == ["guiding-bolt"]
    assert [spell.id for spell in template.defensive_spell_actions] == ["bless", "shield-of-faith"]
    assert [spell.id for spell in template.healing_actions] == ["cure-wounds"]


def test_sacred_flame_uses_character_level_cantrip_scaling() -> None:
    assert build_sacred_flame(13, 1).damage_dice_count == 1
    assert build_sacred_flame(13, 5).damage_dice_count == 2
    assert build_sacred_flame(13, 11).damage_dice_count == 3
    assert build_sacred_flame(13, 17).damage_dice_count == 4
    assert build_sacred_flame(13, 20).damage_dice_count == 4


def test_seraphine_is_exposed_only_through_certified_registry() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 1, "canonical")] == (
        "Seraphine Dawnshield",
        "seraphine-dawnshield-l1",
    )
