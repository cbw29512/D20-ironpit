from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package, prepared_count_2014
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014


def test_level_19_split_asi_and_slot_progression_recompile_derived_values() -> None:
    level18 = build_aurelia_brightshield_2014(18)
    hero = build_aurelia_brightshield_2014(19)
    profile = build_aurelia_brightshield_2014_profile(19)
    combat = build_aurelia_brightshield_2014_combat_profile(19)

    assert hero.level == 19
    assert hero.max_hp == level18.max_hp + 8 == 156
    assert hero.ability_scores.strength == 20
    assert hero.ability_scores.dexterity == 12
    assert hero.ability_scores.constitution == 14
    assert hero.ability_scores.wisdom == 13
    assert hero.ability_scores.charisma == 20
    assert profile.final_ability_scores == combat.abilities == hero.ability_scores
    assert [(item.ability, item.amount) for item in profile.advancement_increases[-2:]] == [
        ("charisma", 1), ("dexterity", 1),
    ]

    assert hero.initiative_bonus == 1
    assert hero.progression_features.aura_radius_2014_ft == 30
    assert hero.progression_features.aura_of_protection_2014_bonus == 5
    assert hero.progression_features.sacred_weapon_2014_bonus == 5
    assert hero.skill_bonuses["persuasion"] == 11
    assert hero.saving_throw_bonuses["dexterity"] == 1
    assert hero.saving_throw_bonuses["charisma"] == 11

    resources = {item.id: item.max_uses for item in hero.resources}
    assert [resources[f"spell-slot-{level}"] for level in range(1, 6)] == [4, 3, 3, 3, 2]
    assert resources["lay-on-hands"] == 95
    assert resources["cleansing-touch"] == 5

    assert len(hero.spell_save_actions) == 1
    flame_strike = hero.spell_save_actions[0]
    assert flame_strike.id == "flame-strike"
    assert flame_strike.dc == 19
    assert [(part.dice_count, part.dice_size, part.damage_type) for part in flame_strike.damage_components] == [
        (4, 6, "fire"), (4, 6, "radiant"),
    ]

    charisma_modifier = hero.ability_scores.modifier("charisma")
    assert prepared_count_2014(19, charisma_modifier) == 14
    package = build_paladin_2014_spell_package(19, charisma_modifier)
    assert package is not None
    assert len(package.spells) == 14
    raise_dead = next(spell for spell in package.spells if spell.id == "raise-dead")
    assert raise_dead.spell_level == 5
    assert raise_dead.required_capabilities == ["arena-out-of-scope"]

    audit = next(item for item in profile.feature_audits if item.feature_id == "ability-score-improvement-l19")
    assert audit.automated is True
    assert "+1 Charisma, +1 Dexterity" in audit.feature_name

    assert_character_resources_raw_ready(hero, profile, combat)
