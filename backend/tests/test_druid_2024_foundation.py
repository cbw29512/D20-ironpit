from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package


def test_2024_druid_level_one_is_legal_magician_foundation() -> None:
    profile = build_thalen_greenbough_profile(1)
    hero = build_thalen_greenbough_level(1)

    assert_canonical_profile_policy(profile)
    assert profile.ruleset == "2024"
    assert profile.class_id == "druid"
    assert profile.subclass_id is None
    assert profile.subclass_name is None
    assert profile.species_id == "wood-elf"
    assert profile.background_id == "acolyte"
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma, hero.ability_scores.intelligence) == (17, 15, 13)
    assert (hero.ability_scores.strength, hero.ability_scores.dexterity, hero.ability_scores.constitution) == (10, 10, 10)
    assert hero.armor_class == 13
    assert hero.max_hp == 8
    assert hero.speed_ft == 35
    assert hero.weapon_attack is not None
    assert hero.weapon_attack.weapon.id == "sickle"
    assert hero.weapon_attack.weapon.mastery_property is None
    assert hero.weapon_attack.attack_bonus == 2
    assert hero.saving_throw_bonuses["intelligence"] == 3
    assert hero.saving_throw_bonuses["wisdom"] == 5
    assert hero.skill_bonuses["nature"] == 6
    assert hero.skill_bonuses["perception"] == 5
    assert {item.id: item.max_uses for item in hero.resources} == {"spell-slot-1": 2}


def test_2024_druid_level_one_has_no_early_circle_of_land_features() -> None:
    profile = build_thalen_greenbough_profile(1)

    assert profile.subclass_id is None
    assert all("circle" not in item.feature_id for item in profile.feature_audits)
    assert all("land" not in item.feature_id for item in profile.feature_audits)


def test_2024_druid_level_one_reuses_universal_fey_ancestry() -> None:
    hero = build_thalen_greenbough_level(1)

    grants = hero.progression_features.saving_throw_advantage_grants
    assert len(grants) == 1
    grant = grants[0]
    assert grant.source_id == "fey-ancestry"
    assert set(grant.abilities) == {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
    }
    assert grant.required_effect_tags == ["charm"]


def test_2024_druid_level_one_spell_package_is_edition_correct() -> None:
    package = canonical_spell_package("druid", 1, "2024", 3)

    assert package is not None
    assert [item.id for item in package.cantrips] == [
        "poison-spray", "elementalism", "mending",
    ]
    assert [item.id for item in package.spells] == [
        "healing-word", "cure-wounds", "longstrider", "detect-magic",
    ]
    assert [item.id for item in package.always_prepared_spells] == [
        "speak-with-animals",
    ]

    hero = build_thalen_greenbough_level(1)
    poison = hero.spell_attack_actions[0]
    assert (
        poison.id,
        poison.action_cost,
        poison.attack_kind,
        poison.range_ft,
        poison.attack_bonus,
        poison.damage_dice_count,
        poison.damage_dice_size,
        poison.damage_type,
    ) == ("poison-spray", "action", "ranged", 30, 5, 1, 12, "poison")

    assert [item.id for item in hero.healing_actions] == ["healing-word", "cure-wounds"]
    healing_word, cure_wounds = hero.healing_actions
    assert (healing_word.dice_count, healing_word.dice_size, healing_word.healing_bonus) == (2, 4, 3)
    assert (cure_wounds.dice_count, cure_wounds.dice_size, cure_wounds.healing_bonus) == (2, 8, 3)

    longstrider = hero.defensive_spell_actions[0]
    assert (
        longstrider.id,
        longstrider.action_cost,
        longstrider.range_ft,
        longstrider.duration_minutes,
        longstrider.target_count,
        longstrider.target_count_per_slot_above,
        longstrider.concentration,
    ) == ("longstrider", "action", 5, 60, 1, 1, False)


def test_2024_druid_level_two_adds_raw_wild_shape_and_faerie_fire() -> None:
    profile = build_thalen_greenbough_profile(2)
    hero = build_thalen_greenbough_level(2)
    package = canonical_spell_package("druid", 2, "2024", 3)

    assert_canonical_profile_policy(profile)
    assert profile.level == 2
    assert profile.subclass_id is None
    assert hero.max_hp == 13
    assert hero.creature_type == "Humanoid"
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 3,
        "wild-shape": 2,
    }
    assert package is not None
    assert [item.id for item in package.spells] == [
        "healing-word", "cure-wounds", "longstrider", "detect-magic", "faerie-fire",
    ]

    action = hero.replacement_form_actions[0]
    assert (
        action.id,
        action.action_cost,
        action.form_template_id,
        action.resource_id,
        action.hp_mode,
        action.temporary_hp_on_enter,
        action.retain_creature_type,
        action.ends_on_incapacitated,
        action.replace_existing_form,
        action.retain_spellcasting,
    ) == ("wild-shape", "bonus_action", "srd-wolf", "wild-shape", "retain_owner", 2, True, True, True, False)

    faerie_fire = hero.spell_save_actions[0]
    assert (
        faerie_fire.id,
        faerie_fire.action_cost,
        faerie_fire.range_ft,
        faerie_fire.area.shape if faerie_fire.area else None,
        faerie_fire.area.origin if faerie_fire.area else None,
        faerie_fire.area.length_ft if faerie_fire.area else None,
        faerie_fire.save_ability,
        faerie_fire.concentration,
        faerie_fire.duration_minutes,
    ) == ("faerie-fire", "action", 60, "cube", "point", 20, "dexterity", True, 1)
    assert {item.kind for item in faerie_fire.failed_save_modifier_effects} == {
        "attacks-against-advantage",
        "invisibility-benefits-suppressed",
    }


def test_2024_druid_level_two_preserves_wild_companion_without_summoning() -> None:
    profile = build_thalen_greenbough_profile(2)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["wild-shape"].combat_relevant is True
    assert audits["wild-shape"].automated is True
    assert audits["wild-companion"].combat_relevant is False
    assert audits["wild-companion"].automated is False
    assert "arena-unavailable" in (audits["wild-companion"].notes or "")


def test_2024_circle_of_land_level_three_is_raw_and_arid() -> None:
    profile = build_thalen_greenbough_profile(3)
    hero = build_thalen_greenbough_level(3)
    package = canonical_spell_package("druid", 3, "2024", 3)

    assert_canonical_profile_policy(profile)
    assert (profile.subclass_id, profile.subclass_name) == ("circle-land", "Circle of the Land")
    assert hero.max_hp == 18
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 2,
        "wild-shape": 2,
    }

    assert package is not None
    assert [item.id for item in package.spells] == [
        "healing-word", "cure-wounds", "longstrider", "detect-magic",
        "faerie-fire", "lesser-restoration",
    ]

    assert [item.id for item in hero.spell_attack_actions] == ["poison-spray", "fire-bolt"]
    fire_bolt = hero.spell_attack_actions[1]
    assert (
        fire_bolt.action_cost, fire_bolt.range_ft, fire_bolt.attack_bonus,
        fire_bolt.damage_dice_count, fire_bolt.damage_dice_size, fire_bolt.damage_type,
    ) == ("action", 120, 5, 1, 10, "fire")

    assert [item.id for item in hero.spell_save_actions] == ["faerie-fire", "burning-hands"]
    burning_hands = hero.spell_save_actions[1]
    assert (
        burning_hands.level, burning_hands.range_ft,
        burning_hands.area.shape if burning_hands.area else None,
        burning_hands.area.origin if burning_hands.area else None,
        burning_hands.area.length_ft if burning_hands.area else None,
        burning_hands.save_ability, burning_hands.dc,
        burning_hands.damage_dice_count, burning_hands.damage_dice_size,
        burning_hands.damage_type, burning_hands.success_damage,
        burning_hands.upcast_dice_per_level,
    ) == (1, 15, "cone", "self", 15, "dexterity", 13, 3, 6, "fire", "half", 1)

    assert [item.id for item in hero.defensive_spell_actions] == ["longstrider", "blur"]
    blur = hero.defensive_spell_actions[1]
    assert blur.concentration is True
    assert blur.target_policy == "self"
    assert blur.modifier_effects[0].kind == "attacks-against-disadvantage"
    assert blur.modifier_effects[0].bypass_attacker_senses == ["blindsight", "truesight"]

    assert [item.id for item in hero.condition_removal_actions] == ["lesser-restoration"]
    lesser = hero.condition_removal_actions[0]
    assert (lesser.action_cost, lesser.range_ft, lesser.resource_costs) == (
        "bonus_action", 5, {"spell-slot-2": 1},
    )

    assert [item.id for item in hero.saving_throw_actions] == ["lands-aid"]
    lands_aid = hero.saving_throw_actions[0]
    assert (
        lands_aid.action_cost, lands_aid.range_ft,
        lands_aid.area.shape if lands_aid.area else None,
        lands_aid.area.radius_ft if lands_aid.area else None,
        lands_aid.save_ability, lands_aid.dc,
        lands_aid.damage_dice_count, lands_aid.damage_dice_size,
        lands_aid.damage_type, lands_aid.success_damage,
        lands_aid.resource_id, lands_aid.resource_cost,
    ) == ("action", 60, "radius", 10, "constitution", 13, 2, 6, "necrotic", "half", "wild-shape", 1)
    assert lands_aid.area_healing_rider is not None
    assert (
        lands_aid.area_healing_rider.dice_count,
        lands_aid.area_healing_rider.dice_size,
    ) == (2, 6)

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["lands-aid"].automated is True
    assert audits["land-arid-spells"].automated is True


def test_2024_druid_level_four_applies_wisdom_asi_and_starry_wisp() -> None:
    profile = build_thalen_greenbough_profile(4)
    hero = build_thalen_greenbough_level(4)
    package = canonical_spell_package("druid", 4, "2024", 4)

    assert_canonical_profile_policy(profile)
    assert profile.subclass_id == "circle-land"
    assert profile.final_ability_scores.wisdom == 19
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [("wisdom", 2)]
    assert hero.max_hp == 23
    assert hero.saving_throw_bonuses["wisdom"] == 6
    assert hero.skill_bonuses["nature"] == 7
    assert hero.skill_bonuses["survival"] == 6
    assert hero.skill_bonuses["perception"] == 6
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "wild-shape": 2,
    }

    assert package is not None
    assert [item.id for item in package.cantrips] == [
        "poison-spray", "elementalism", "mending", "starry-wisp",
    ]
    assert [item.id for item in package.spells] == [
        "healing-word", "cure-wounds", "longstrider", "detect-magic",
        "faerie-fire", "lesser-restoration", "detect-poison-disease",
    ]

    assert [item.id for item in hero.spell_attack_actions] == [
        "poison-spray", "fire-bolt", "starry-wisp",
    ]
    poison, fire_bolt, starry = hero.spell_attack_actions
    assert poison.attack_bonus == 6
    assert fire_bolt.attack_bonus == 6
    assert (
        starry.action_cost, starry.range_ft, starry.attack_bonus,
        starry.damage_dice_count, starry.damage_dice_size, starry.damage_type,
    ) == ("action", 60, 6, 1, 8, "radiant")
    assert len(starry.on_hit_modifier_effects) == 1
    rider = starry.on_hit_modifier_effects[0]
    assert rider.kind == "invisibility-benefits-suppressed"
    assert rider.expires_after_source_turns == 1

    assert hero.saving_throw_actions[0].dc == 14
    assert all(item.dc == 14 for item in hero.spell_save_actions)
    assert hero.replacement_form_actions[0].temporary_hp_on_enter == 4

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["ability-score-improvement-l4"].automated is True
