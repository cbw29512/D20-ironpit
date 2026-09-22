from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level15_profile,
    build_seraphine_dawnshield_level16_profile,
)
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def test_level_fifteen_uses_simple_eighth_level_upcasts() -> None:
    level14 = build_seraphine_dawnshield_level(14)
    hero = build_seraphine_dawnshield_level(15)
    profile = build_seraphine_dawnshield_level15_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 15)

    assert hero.max_hp == level14.max_hp + 5 == 78
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 17)
    assert _resources(hero) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "channel-divinity": 3,
        "divine-intervention": 1,
        "adrenaline-rush": 5,
        "relentless-endurance": 1,
    }

    damage = next(item for item in hero.spell_save_actions if item.id == "inflict-wounds-l8")
    healing = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds-l8")
    assert (damage.level, damage.damage_dice_count, damage.damage_dice_size) == (8, 9, 10)
    assert (damage.damage_type, damage.success_damage, damage.dc) == ("necrotic", "half", 18)
    assert (healing.dice_count, healing.dice_size, healing.healing_bonus) == (8, 8, 15)
    assert healing.resource_id == "spell-slot-8"

    assert len(package.spells) == 18
    assert package.spells[-1].id == "sunburst"

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["cleric-combat-spells-8"].automated is True
    assert audits["inflict-wounds-upcast-l8"].automated is True
    assert audits["mass-cure-wounds-upcast-l8"].automated is True
    assert audits["sunburst"].combat_relevant is False

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_sixteen_updates_charisma_without_changing_spellcasting_stat() -> None:
    level15 = build_seraphine_dawnshield_level(15)
    hero = build_seraphine_dawnshield_level(16)
    profile = build_seraphine_dawnshield_level16_profile()
    combat = build_pregen_combat_profiles()[hero.id]

    assert hero.max_hp == level15.max_hp + 5 == 83
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 19)
    assert hero.spell_save_actions[-1].id == "inflict-wounds-l8"
    assert hero.healing_actions[-1].id == "mass-cure-wounds-l8"
    assert hero.saving_throw_bonuses["wisdom"] == 10
    assert hero.saving_throw_bonuses["charisma"] == 9
    assert hero.skill_bonuses["medicine"] == 10
    assert hero.skill_bonuses["persuasion"] == 9

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l16"].automated is True

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_certified_registry_exposes_cleric_levels_fifteen_and_sixteen() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 15, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l15",
    )
    assert registry[("cleric", 16, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l16",
    )
    assert ("cleric", 17, "canonical") not in registry
