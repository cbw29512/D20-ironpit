from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_profile import (
    build_seraphine_dawnshield_level7_profile,
    build_seraphine_dawnshield_level8_profile,
)
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def _sacred_flame(template):
    return next(item for item in template.spell_save_actions if item.id == "sacred-flame")


def _mass_healing_word(template):
    return next(item for item in template.healing_actions if item.id == "mass-healing-word")


def test_level_seven_is_incremental_and_uses_potent_spellcasting() -> None:
    level6 = build_seraphine_dawnshield_level(6)
    hero = build_seraphine_dawnshield_level(7)
    profile = build_seraphine_dawnshield_level7_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 7)

    assert hero.max_hp == level6.max_hp + 5 == 38
    assert hero.ability_scores.wisdom == 19
    assert hero.ability_scores.charisma == 14
    assert _resources(hero) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
        "channel-divinity": 3,
        "adrenaline-rush": 3,
        "relentless-endurance": 1,
    }

    sacred_flame = _sacred_flame(hero)
    assert (sacred_flame.damage_dice_count, sacred_flame.damage_dice_size) == (2, 8)
    assert sacred_flame.damage_bonus == 4
    assert sacred_flame.dc == 15
    assert hero.spell_attack_actions[0].attack_bonus == 7
    assert _mass_healing_word(hero).healing_bonus == 9

    assert package is not None
    assert len(package.spells) == 11
    assert package.spells[-1].id == "prayer-of-healing"
    assert [spell.id for spell in package.always_prepared_spells][-2:] == [
        "aura-of-life", "death-ward",
    ]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["blessed-strikes"].automated is True
    assert audits["cleric-combat-spells-4"].combat_relevant is False
    assert audits["prayer-of-healing"].combat_relevant is False

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_eight_applies_split_asi_and_keeps_simple_spell_policy() -> None:
    level7 = build_seraphine_dawnshield_level(7)
    hero = build_seraphine_dawnshield_level(8)
    profile = build_seraphine_dawnshield_level8_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 8)

    assert hero.max_hp == level7.max_hp + 5 == 43
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 15)
    assert _resources(hero) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 2,
        "channel-divinity": 3,
        "adrenaline-rush": 3,
        "relentless-endurance": 1,
    }

    sacred_flame = _sacred_flame(hero)
    assert (sacred_flame.damage_dice_count, sacred_flame.damage_dice_size) == (2, 8)
    assert sacred_flame.damage_bonus == 5
    assert sacred_flame.dc == 16
    assert hero.spell_attack_actions[0].attack_bonus == 8
    assert _mass_healing_word(hero).healing_bonus == 10
    assert hero.saving_throw_bonuses["wisdom"] == 8
    assert hero.skill_bonuses["medicine"] == 8

    assert package is not None
    assert len(package.spells) == 12
    assert [spell.id for spell in package.spells][-2:] == [
        "prayer-of-healing", "guardian-of-faith",
    ]
    assert [spell.id for spell in package.always_prepared_spells][-2:] == [
        "aura-of-life", "death-ward",
    ]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l8"].automated is True
    assert audits["guardian-of-faith"].combat_relevant is False

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_certified_registry_exposes_cleric_levels_seven_and_eight() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 7, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l7",
    )
    assert registry[("cleric", 8, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l8",
    )
    assert ("cleric", 9, "canonical") not in registry
