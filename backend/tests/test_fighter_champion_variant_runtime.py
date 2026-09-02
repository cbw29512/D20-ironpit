from app.content.build_audit import assert_character_build_raw_ready, audit_character_build
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
    assert greatsword.weapon.id == "greatsword"
    assert (greatsword.weapon.mastery_property, greatsword.weapon.heavy, greatsword.weapon.two_handed) == ("Graze", True, True)
    assert (greatsword.attack_bonus, greatsword.damage_bonus, greatsword.damage_die_minimum) == (5, 3, 3)
    assert greatsword.attack_ability == "strength"
    assert len(template.attack_action.slots) == 1
    assert_character_build_raw_ready(profile, template)


def test_champion_level_seven_additional_defense_changes_great_weapon_ac() -> None:
    template = compile_fighter_champion_variant("great-weapon", 7)
    assert template.armor_class == 17
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
    assert longsword.attack_bonus == 6
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
    assert template.armor_class == 16


def test_dual_wield_sheet_is_complete_but_runtime_readiness_fails_on_twf_support() -> None:
    profile = build_fighter_champion_variant_profile("dual-wield", 3)
    template = compile_fighter_champion_variant("dual-wield", 3)
    assert template.armor_class == 15
    assert template.visual.main_hand == "scimitar"
    assert template.visual.off_hand == "shortsword"
    assert template.weapon_attack.weapon.light is True
    assert "scimitar" in template.weapon_masteries
    assert "shortsword" in template.weapon_masteries
    issues = audit_character_build(profile, template)
    assert "combat-feature-not-automated:fighting-style-two-weapon-fighting" in issues


def test_attack_action_slot_count_comes_only_from_fighter_level() -> None:
    expected = {3: 1, 5: 2, 11: 3, 20: 4}
    for build_id in ("great-weapon", "sword-shield", "archer", "dual-wield"):
        for level, count in expected.items():
            template = compile_fighter_champion_variant(build_id, level)
            assert template.attack_action.is_attack_action is True
            assert len(template.attack_action.slots) == count


def test_high_level_character_truth_blocks_readiness_instead_of_dropping_features() -> None:
    profile = build_fighter_champion_variant_profile("great-weapon", 10)
    template = compile_fighter_champion_variant("great-weapon", 10)
    issues = audit_character_build(profile, template)
    assert "combat-feature-not-automated:tactical-master" in issues
    assert "combat-feature-not-automated:heroic-warrior" in issues
