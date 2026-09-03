from app.content.combat_build_choice_overlays import (
    BARBARIAN_COMBAT_BUILD_CHOICES,
    BARD_COMBAT_BUILD_CHOICES,
    COMBAT_BUILD_CHOICE_OVERLAYS,
    FIGHTER_COMBAT_BUILD_CHOICES,
    MONK_COMBAT_BUILD_CHOICES,
    PALADIN_COMBAT_BUILD_CHOICES,
    RANGER_COMBAT_BUILD_CHOICES,
    ROGUE_COMBAT_BUILD_CHOICES,
    SORCERER_COMBAT_BUILD_CHOICES,
    WIZARD_COMBAT_BUILD_CHOICES,
    WARLOCK_COMBAT_BUILD_CHOICES,
    get_combat_build_choice_overlay,
)
from app.content.combat_build_variants import get_combat_build_variant


def test_all_fighter_role_variants_have_choice_overlays() -> None:
    expected = {"great-weapon", "sword-shield", "archer", "dual-wield"}
    assert set(FIGHTER_COMBAT_BUILD_CHOICES) == expected
    assert {get_combat_build_variant("fighter", build_id).id for build_id in expected} == expected


def test_fighter_builds_share_progression_but_make_distinct_role_choices() -> None:
    great = get_combat_build_choice_overlay("fighter", "great-weapon")
    shield = get_combat_build_choice_overlay("fighter", "sword-shield")
    archer = get_combat_build_choice_overlay("fighter", "archer")
    dual = get_combat_build_choice_overlay("fighter", "dual-wield")

    assert (great.primary_ability, great.fighting_style, great.primary_weapon) == (
        "strength", "Great Weapon Fighting", "greatsword",
    )
    assert shield.shield is True and shield.primary_weapon == "longsword"
    assert (archer.primary_ability, archer.fighting_style, archer.primary_weapon) == (
        "dexterity", "Archery", "longbow",
    )
    assert (dual.primary_ability, dual.fighting_style, dual.primary_weapon) == (
        "dexterity", "Two-Weapon Fighting", "shortsword",
    )


def test_dual_wield_fighter_declares_nick_and_vex_as_shared_engine_requirements() -> None:
    dual = get_combat_build_choice_overlay("fighter", "dual-wield")
    assert dual.weapon_masteries[:2] == ("shortsword", "scimitar")
    assert dual.secondary_weapons[0] == "scimitar"
    assert {"nick-mastery", "vex-mastery"} <= set(dual.required_capabilities)


def test_archer_does_not_turn_slow_into_an_arena_engine_requirement() -> None:
    archer = get_combat_build_choice_overlay("fighter", "archer")
    assert "slow-mastery" in archer.arena_ignored
    assert "slow-mastery" not in archer.required_capabilities


def test_sword_and_shield_is_a_real_distinct_defender_overlay() -> None:
    shield = get_combat_build_choice_overlay("fighter", "sword-shield")
    assert shield.armor == "chain-mail"
    assert shield.shield is True
    assert shield.fighting_style == "Defense"
    assert "sap-mastery" in shield.required_capabilities


def test_barbarian_subclass_specializations_generate_real_choice_overlays() -> None:
    assert set(BARBARIAN_COMBAT_BUILD_CHOICES) == {"great-weapon", "weapon-shield", "dual-wield"}
    berserker = get_combat_build_choice_overlay("barbarian", "great-weapon")
    wild_heart = get_combat_build_choice_overlay("barbarian", "weapon-shield")
    zealot = get_combat_build_choice_overlay("barbarian", "dual-wield")
    assert (berserker.primary_weapon, berserker.weapon_masteries[:2]) == (
        "greataxe", ("greataxe", "battleaxe"),
    )
    assert wild_heart.primary_weapon == "battleaxe" and wild_heart.shield is True
    assert zealot.primary_ability == "strength"
    assert zealot.secondary_weapons[0] == "scimitar"
    assert {"vex-mastery", "nick-mastery"} <= set(zealot.required_capabilities)


def test_all_current_choice_overlays_come_from_subclass_specializations() -> None:
    assert len(COMBAT_BUILD_CHOICE_OVERLAYS) == 31
    assert all("derived from" in overlay.notes for overlay in COMBAT_BUILD_CHOICE_OVERLAYS.values())


def test_monk_specializations_do_not_invent_weapon_mastery_or_fighting_styles() -> None:
    assert set(MONK_COMBAT_BUILD_CHOICES) == {
        "unarmed-offense", "weapon-monk", "defensive-mobile",
    }
    open_hand = get_combat_build_choice_overlay("monk", "unarmed-offense")
    shadow = get_combat_build_choice_overlay("monk", "weapon-monk")
    elements = get_combat_build_choice_overlay("monk", "defensive-mobile")
    assert open_hand.primary_weapon is None
    assert shadow.primary_weapon == "shortsword"
    assert elements.primary_weapon is None
    assert all(not item.weapon_masteries for item in MONK_COMBAT_BUILD_CHOICES.values())
    assert all(item.fighting_style is None for item in MONK_COMBAT_BUILD_CHOICES.values())


def test_paladin_oaths_generate_distinct_loadouts_from_shared_rules() -> None:
    assert set(PALADIN_COMBAT_BUILD_CHOICES) == {"great-weapon", "sword-shield", "support-healer"}
    devotion = get_combat_build_choice_overlay("paladin", "sword-shield")
    vengeance = get_combat_build_choice_overlay("paladin", "great-weapon")
    ancients = get_combat_build_choice_overlay("paladin", "support-healer")
    assert (devotion.primary_weapon, devotion.shield, devotion.fighting_style) == (
        "longsword", True, "Defense",
    )
    assert (vengeance.primary_weapon, vengeance.shield, vengeance.fighting_style) == (
        "greatsword", False, "Great Weapon Fighting",
    )
    assert (ancients.primary_weapon, ancients.shield, ancients.fighting_style) == (
        "battleaxe", True, "Defense",
    )
    assert devotion.weapon_masteries == ("longsword", "battleaxe")
    assert vengeance.weapon_masteries == ("greatsword", "longsword")
    assert ancients.weapon_masteries == ("battleaxe", "longsword")
    assert "sap-mastery" in devotion.required_capabilities
    assert "graze-mastery" in vengeance.required_capabilities
    assert "topple-mastery" in ancients.required_capabilities


def test_ranger_subclasses_generate_distinct_loadouts_from_shared_rules() -> None:
    assert set(RANGER_COMBAT_BUILD_CHOICES) == {"archer", "dual-wield", "sword-shield"}
    gloom = get_combat_build_choice_overlay("ranger", "archer")
    beast = get_combat_build_choice_overlay("ranger", "dual-wield")
    hunter = get_combat_build_choice_overlay("ranger", "sword-shield")
    assert (gloom.primary_weapon, gloom.fighting_style) == ("longbow", "Archery")
    assert "slow-mastery" in gloom.arena_ignored
    assert (hunter.primary_weapon, hunter.shield, hunter.fighting_style) == (
        "shortsword", True, "Defense",
    )
    assert beast.secondary_weapons[:2] == ("scimitar", "longbow")
    assert beast.weapon_masteries == ("shortsword", "scimitar")
    assert {"vex-mastery", "nick-mastery"} <= set(beast.required_capabilities)


def test_rogue_subclasses_generate_distinct_loadouts_from_shared_rules() -> None:
    assert set(ROGUE_COMBAT_BUILD_CHOICES) == {"duelist", "dual-wield", "ranged"}
    trickster = get_combat_build_choice_overlay("rogue", "duelist")
    thief = get_combat_build_choice_overlay("rogue", "dual-wield")
    assassin = get_combat_build_choice_overlay("rogue", "ranged")
    assert (trickster.primary_weapon, trickster.weapon_masteries) == (
        "rapier", ("rapier", "shortbow"),
    )
    assert thief.secondary_weapons[:2] == ("scimitar", "shortbow")
    assert {"vex-mastery", "nick-mastery"} <= set(thief.required_capabilities)
    assert (assassin.primary_weapon, assassin.weapon_masteries) == (
        "shortbow", ("shortbow", "shortsword"),
    )


def test_wizard_subclasses_generate_spell_package_compatibility_views() -> None:
    assert set(WIZARD_COMBAT_BUILD_CHOICES) == {"fire-damage", "frost-control", "mixed-arcane"}
    evoker = get_combat_build_choice_overlay("wizard", "fire-damage")
    illusionist = get_combat_build_choice_overlay("wizard", "frost-control")
    abjurer = get_combat_build_choice_overlay("wizard", "mixed-arcane")
    assert (evoker.primary_ability, evoker.spell_package_id) == ("intelligence", "evoker")
    assert illusionist.spell_package_id == "illusionist"
    assert abjurer.spell_package_id == "abjurer"
    assert all(item.focus_item == "arcane-focus" for item in WIZARD_COMBAT_BUILD_CHOICES.values())
    assert all(item.primary_weapon is None for item in WIZARD_COMBAT_BUILD_CHOICES.values())


def test_sorcerer_subclasses_generate_spell_package_compatibility_views() -> None:
    assert set(SORCERER_COMBAT_BUILD_CHOICES) == {"fire-damage", "frost-control", "mixed-arcane"}
    assert get_combat_build_choice_overlay("sorcerer", "fire-damage").spell_package_id == "draconic-sorcery"
    assert get_combat_build_choice_overlay("sorcerer", "frost-control").spell_package_id == "aberrant-sorcery"
    assert get_combat_build_choice_overlay("sorcerer", "mixed-arcane").spell_package_id == "clockwork-sorcery"
    assert all(item.focus_item == "arcane-focus" for item in SORCERER_COMBAT_BUILD_CHOICES.values())


def test_warlock_patron_specializations_generate_distinct_compatibility_views() -> None:
    assert set(WARLOCK_COMBAT_BUILD_CHOICES) == {"blaster", "controller", "blade-hybrid"}
    assert get_combat_build_choice_overlay("warlock", "blaster").spell_package_id == "fiend-patron"
    assert get_combat_build_choice_overlay("warlock", "controller").spell_package_id == "great-old-one-patron"
    blade = get_combat_build_choice_overlay("warlock", "blade-hybrid")
    assert (blade.spell_package_id, blade.primary_weapon) == ("celestial-patron", "shortsword")
    assert not blade.weapon_masteries


def test_bard_colleges_generate_distinct_compatibility_views() -> None:
    assert set(BARD_COMBAT_BUILD_CHOICES) == {"support-healer", "controller", "battle-bard"}
    assert get_combat_build_choice_overlay("bard", "support-healer").spell_package_id == "college-lore"
    assert get_combat_build_choice_overlay("bard", "controller").spell_package_id == "college-glamour"
    battle = get_combat_build_choice_overlay("bard", "battle-bard")
    assert (battle.spell_package_id, battle.primary_weapon, battle.shield) == (
        "college-valor", "rapier", True,
    )
