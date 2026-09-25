from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package, prepared_count_2014
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014


def test_level_16_is_incremental_charisma_asi_progression() -> None:
    level15 = build_aurelia_brightshield_2014(15)
    hero = build_aurelia_brightshield_2014(16)
    profile = build_aurelia_brightshield_2014_profile(16)
    combat_profile = build_aurelia_brightshield_2014_combat_profile(16)

    # Level 16 changes the existing character; it does not rebuild Aurelia.
    assert hero.level == 16
    assert hero.max_hp == level15.max_hp + 8
    assert hero.ability_scores.strength == level15.ability_scores.strength == 20
    assert level15.ability_scores.charisma == 17
    assert hero.ability_scores.charisma == 19
    assert profile.final_ability_scores == hero.ability_scores
    assert (profile.advancement_increases[-1].ability, profile.advancement_increases[-1].amount) == ("charisma", 2)

    # All Charisma-derived combat facts must update from the shared score source.
    assert hero.progression_features.aura_of_protection_2014_bonus == 4
    assert hero.progression_features.sacred_weapon_2014_bonus == 4
    assert hero.skill_bonuses["persuasion"] == 9
    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["cleansing-touch"] == 4
    assert resources["lay-on-hands"] == 80
    assert [resources[f"spell-slot-{level}"] for level in range(1, 5)] == [4, 3, 3, 2]

    # Purity of Spirit and all prior level-15 mechanics persist unchanged.
    assert hero.passive_modifier_grants == level15.passive_modifier_grants
    assert {item.id for item in hero.effect_removal_actions} == {"cleansing-touch", "dispel-magic"}

    assert_character_resources_raw_ready(hero, profile, combat_profile)


def test_level_16_prepared_spell_capacity_is_legally_filled() -> None:
    hero = build_aurelia_brightshield_2014(16)
    charisma_modifier = hero.ability_scores.modifier("charisma")

    assert charisma_modifier == 4
    assert prepared_count_2014(16, charisma_modifier) == 12

    package = build_paladin_2014_spell_package(16, charisma_modifier)
    assert package is not None
    assert len(package.spells) == 12

    ids = {spell.id for spell in package.spells}
    assert "find-steed" in ids
    assert "create-food-and-water" in ids
    assert "death-ward" in ids
    assert "purify-food-and-drink" not in ids

    find_steed = next(spell for spell in package.spells if spell.id == "find-steed")
    create_food = next(spell for spell in package.spells if spell.id == "create-food-and-water")
    assert find_steed.required_capabilities == ["arena-unavailable-summon"]
    assert create_food.required_capabilities == ["arena-out-of-scope"]
