from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
from app.content.capability_compiler import compile_combatant
from app.content.capability_from_template import definition_from_template
from app.content.fighter_champion_variant_profiles import build_fighter_champion_variant_profile
from app.content.fighter_champion_variant_runtime import compile_fighter_champion_variant


def _attack(template, weapon_id: str):
    return next(
        attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
        if attack.weapon.id == weapon_id
    )


def test_level_three_great_weapon_compiles_from_character_truth() -> None:
    profile = build_fighter_champion_variant_profile("great-weapon", 3)
    template = compile_fighter_champion_variant("great-weapon", 3)
    greatsword = template.weapon_attack
    assert (template.armor_class, template.max_hp) == (16, 28)
    assert template.ability_scores == profile.final_ability_scores
    assert template.weapon_masteries == profile.weapon_masteries
    assert template.fighting_styles == profile.fighting_styles == ["Great Weapon Fighting"]
    assert greatsword.weapon.id == "greatsword"
    assert (greatsword.weapon.mastery_property, greatsword.weapon.heavy, greatsword.weapon.two_handed) == ("Graze", True, True)
    assert (greatsword.attack_bonus, greatsword.damage_bonus, greatsword.damage_die_minimum) == (5, 3, 3)
    assert greatsword.attack_ability == "strength"
    assert len(template.attack_action.slots) == 1
    assert_character_build_raw_ready(profile, template)


def test_champion_level_seven_additional_defense_changes_great_weapon_ac() -> None:
    template = compile_fighter_champion_variant("great-weapon", 7)
    assert template.armor_class == 17
    assert template.fighting_styles == ["Great Weapon Fighting", "Defense"]
    assert template.progression_features.great_weapon_fighting is True


def test_level_three_sword_shield_compiles_defense_shield_and_sap() -> None:
    profile = build_fighter_champion_variant_profile("sword-shield", 3)
    template = compile_fighter_champion_variant("sword-shield", 3)
    longsword = template.weapon_attack
    assert template.armor_class == 19
    assert template.visual.off_hand == "shield"
    assert longsword.weapon.id == "longsword"
    assert (longsword.weapon.mastery_property, longsword.weapon.versatile) == ("Sap", True)
    assert (longsword.attack_bonus, longsword.damage_bonus) == (5, 3)
    assert_character_build_raw_ready(profile, template)


def test_sword_shield_level_seven_archery_style_applies_to_ranged_backup_only() -> None:
    template = compile_fighter_champion_variant("sword-shield", 7)
    longsword = _attack(template, "longsword")
    shortbow = _attack(template, "shortbow")
    assert template.fighting_styles == ["Defense", "Archery"]
    assert longsword.attack_bonus == 8
    assert shortbow.attack_bonus == 6
    assert shortbow.attack_bonus - (3 + 1) == 2


def test_level_three_archer_uses_dexterity_longbow_and_light_backup_truth() -> None:
    template = compile_fighter_champion_variant("archer", 3)
    longbow = _attack(template, "longbow")
    scimitar = _attack(template, "scimitar")
    shortsword = _attack(template, "shortsword")
    assert template.armor_class == 15
    assert (longbow.attack_bonus, longbow.damage_bonus, longbow.attack_ability) == (7, 3, "dexterity")
    assert (scimitar.weapon.light, scimitar.weapon.finesse, scimitar.weapon.mastery_property) == (True, True, "Nick")
    assert (shortsword.weapon.light, shortsword.weapon.finesse, shortsword.weapon.mastery_property) == (True, True, "Vex")
    assert {"longbow", "shortsword", "scimitar"}.issubset(template.weapon_masteries)


def test_archer_level_seven_additional_defense_changes_studded_leather_ac() -> None:
    template = compile_fighter_champion_variant("archer", 7)
    assert template.armor_class == 18
    assert template.ability_scores.dexterity == 20
    assert template.fighting_styles == ["Archery", "Defense"]


def test_dual_wield_sheet_and_runtime_structure_are_complete() -> None:
    profile = build_fighter_champion_variant_profile("dual-wield", 3)
    template = compile_fighter_champion_variant("dual-wield", 3)
    scimitar = _attack(template, "scimitar")
    shortsword = _attack(template, "shortsword")
    assert template.armor_class == 15
    assert template.visual.main_hand == "shortsword"
    assert template.visual.off_hand == "scimitar"
    assert template.weapon_attack.weapon.id == "shortsword"
    assert shortsword.weapon.mastery_property == "Vex"
    assert scimitar.weapon.mastery_property == "Nick"
    assert template.fighting_styles == ["Two-Weapon Fighting"]
    assert "scimitar" in template.weapon_masteries
    assert "shortsword" in template.weapon_masteries
    assert audit_character_build(profile, template) == []


def test_dual_wield_level_seven_preserves_additional_defense_style() -> None:
    template = compile_fighter_champion_variant("dual-wield", 7)
    assert template.fighting_styles == ["Two-Weapon Fighting", "Defense"]
    assert template.armor_class == 18


def test_capability_round_trip_preserves_all_champion_fighting_styles() -> None:
    template = compile_fighter_champion_variant("dual-wield", 7)
    rebuilt = compile_combatant(definition_from_template(template))
    assert rebuilt.fighting_style == "Two-Weapon Fighting"
    assert rebuilt.fighting_styles == ["Two-Weapon Fighting", "Defense"]


def test_attack_action_slot_count_comes_only_from_fighter_level() -> None:
    expected = {3: 1, 5: 2, 11: 3, 20: 4}
    for build_id in ("great-weapon", "sword-shield", "archer", "dual-wield"):
        for level, count in expected.items():
            template = compile_fighter_champion_variant(build_id, level)
            assert template.attack_action.is_attack_action is True
            assert len(template.attack_action.slots) == count


def test_level_ten_keeps_tactical_master_automated_and_blocks_on_heroic_warrior() -> None:
    profile = build_fighter_champion_variant_profile("great-weapon", 10)
    template = compile_fighter_champion_variant("great-weapon", 10)
    assert template.progression_features.tactical_master_sap_weapon_ids == ["greatsword"]
    assert audit_character_build(profile, template) == ["combat-feature-not-automated:heroic-warrior"]
