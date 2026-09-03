import pytest

from app.content.subclass_specializations import (
    BARBARIAN_SPECIALIZATIONS,
    BARD_SPECIALIZATIONS,
    CLERIC_SPECIALIZATIONS,
    DRUID_SPECIALIZATIONS,
    FIGHTER_SPECIALIZATIONS,
    MONK_SPECIALIZATIONS,
    PALADIN_SPECIALIZATIONS,
    RANGER_SPECIALIZATIONS,
    ROGUE_SPECIALIZATIONS,
    SORCERER_SPECIALIZATIONS,
    WIZARD_SPECIALIZATIONS,
    WARLOCK_SPECIALIZATIONS,
    SubclassSpecialization,
    specializations_for_class,
    subclass_specialization,
)
from app.content.weapon_catalog import build_weapon


def test_fighter_has_one_coherent_specialization_per_subclass() -> None:
    by_subclass = {item.subclass_id: item for item in FIGHTER_SPECIALIZATIONS}
    assert set(by_subclass) == {"champion", "battle-master", "eldritch-knight", "psi-warrior"}
    assert by_subclass["champion"].role == "two-handed"
    assert by_subclass["battle-master"].role == "dual-wield"
    assert by_subclass["eldritch-knight"].role == "sword-shield"
    assert by_subclass["psi-warrior"].role == "ranged"


def test_weapon_specializations_are_only_catalog_data_and_mastery_choices() -> None:
    for spec in (
        *FIGHTER_SPECIALIZATIONS,
        *BARBARIAN_SPECIALIZATIONS,
        *BARD_SPECIALIZATIONS,
        *CLERIC_SPECIALIZATIONS,
        *DRUID_SPECIALIZATIONS,
        *MONK_SPECIALIZATIONS,
        *PALADIN_SPECIALIZATIONS,
        *RANGER_SPECIALIZATIONS,
        *ROGUE_SPECIALIZATIONS,
        *SORCERER_SPECIALIZATIONS,
        *WARLOCK_SPECIALIZATIONS,
        *WIZARD_SPECIALIZATIONS,
    ):
        assert spec.source_reference
        if spec.primary_weapon is None:
            assert not spec.secondary_weapons
            assert not spec.mastery_priority
            continue
        weapon = build_weapon(spec.primary_weapon)
        assert weapon.id == spec.primary_weapon
        if spec.mastery_priority:
            assert spec.primary_weapon in spec.mastery_priority
        for weapon_id in spec.secondary_weapons:
            assert build_weapon(weapon_id).id == weapon_id


def test_dual_wield_specialization_gets_vex_and_nick_from_weapons_not_subclass_code() -> None:
    spec = subclass_specialization("battle-master")
    assert build_weapon(spec.primary_weapon).mastery_property == "Vex"
    assert build_weapon(spec.secondary_weapons[0]).mastery_property == "Nick"
    assert spec.fighting_style_priority == ("Two-Weapon Fighting",)


def test_eldritch_knight_is_sword_shield_with_spell_package_pointer() -> None:
    spec = subclass_specialization("eldritch-knight")
    assert (spec.primary_weapon, spec.shield, spec.spell_package_id) == (
        "longsword", True, "eldritch-knight",
    )


def test_barbarian_has_one_strength_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("barbarian")) == (
        "path-berserker", "path-wild-heart", "path-zealot",
    )
    berserker, wild_heart, zealot = BARBARIAN_SPECIALIZATIONS
    assert (berserker.role, berserker.primary_weapon) == ("two-handed", "greataxe")
    assert (wild_heart.role, wild_heart.primary_weapon, wild_heart.shield) == (
        "weapon-shield", "battleaxe", True,
    )
    assert (zealot.role, zealot.primary_weapon, zealot.secondary_weapons[0]) == (
        "dual-wield", "shortsword", "scimitar",
    )
    assert all(item.ability_priority[0] == "strength" for item in BARBARIAN_SPECIALIZATIONS)


def test_barbarian_subclass_choices_are_explicit_specialization_data() -> None:
    wild_heart = subclass_specialization("path-wild-heart")
    zealot = subclass_specialization("path-zealot")
    assert wild_heart.feature_choice_ids == (
        "wild-heart-rage-bear", "wild-heart-aspect-elephant-athletics", "wild-heart-power-lion",
    )
    assert zealot.feature_choice_ids == ("zealot-divine-fury-radiant",)


def test_monk_has_one_dexterity_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("monk")) == (
        "warrior-open-hand", "warrior-shadow", "warrior-elements",
    )
    open_hand, shadow, elements = MONK_SPECIALIZATIONS
    assert (open_hand.role, open_hand.primary_weapon) == ("unarmed-offense", None)
    assert (shadow.role, shadow.primary_weapon) == ("weapon-monk", "shortsword")
    assert (elements.role, elements.primary_weapon) == ("defensive-mobile", None)
    assert all(item.ability_priority[:2] == ("dexterity", "wisdom") for item in MONK_SPECIALIZATIONS)
    assert all(not item.mastery_priority for item in MONK_SPECIALIZATIONS)


def test_paladin_has_one_strength_charisma_specialization_per_target_oath() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("paladin")) == (
        "oath-devotion", "oath-vengeance", "oath-ancients",
    )
    devotion, vengeance, ancients = PALADIN_SPECIALIZATIONS
    assert (devotion.role, devotion.primary_weapon, devotion.shield) == (
        "sword-shield", "longsword", True,
    )
    assert (vengeance.role, vengeance.primary_weapon, vengeance.shield) == (
        "two-handed", "greatsword", False,
    )
    assert (ancients.role, ancients.primary_weapon, ancients.shield) == (
        "support-healing", "battleaxe", True,
    )
    assert all(item.ability_priority[:2] == ("strength", "charisma") for item in PALADIN_SPECIALIZATIONS)
    assert tuple(item.spell_package_id for item in PALADIN_SPECIALIZATIONS) == (
        "oath-devotion", "oath-vengeance", "oath-ancients",
    )


def test_ranger_has_one_dexterity_wisdom_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("ranger")) == (
        "hunter", "gloom-stalker", "beastmaster",
    )
    hunter, gloom, beast = RANGER_SPECIALIZATIONS
    assert (hunter.role, hunter.primary_weapon, hunter.shield) == (
        "durable-melee", "shortsword", True,
    )
    assert (gloom.role, gloom.primary_weapon, gloom.shield) == (
        "ranged", "longbow", False,
    )
    assert (beast.role, beast.primary_weapon, beast.secondary_weapons[:2]) == (
        "dual-wield", "shortsword", ("scimitar", "longbow"),
    )
    assert all(item.ability_priority[:2] == ("dexterity", "wisdom") for item in RANGER_SPECIALIZATIONS)
    assert beast.feature_choice_ids == ("beastmaster-beast-of-the-land",)


def test_rogue_has_one_dexterity_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("rogue")) == (
        "thief", "assassin", "arcane-trickster",
    )
    thief, assassin, trickster = ROGUE_SPECIALIZATIONS
    assert (thief.role, thief.primary_weapon, thief.secondary_weapons[0]) == (
        "dual-wield", "shortsword", "scimitar",
    )
    assert (assassin.role, assassin.primary_weapon) == ("ranged", "shortbow")
    assert (trickster.role, trickster.primary_weapon, trickster.spell_package_id) == (
        "finesse-duelist", "rapier", "arcane-trickster",
    )
    assert all(item.ability_priority[0] == "dexterity" for item in ROGUE_SPECIALIZATIONS)


def test_wizard_has_one_intelligence_spell_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("wizard")) == (
        "evoker", "illusionist", "abjurer",
    )
    assert tuple(item.role for item in WIZARD_SPECIALIZATIONS) == (
        "fire-blaster", "control", "balanced-arcane",
    )
    assert all(item.ability_priority == ("intelligence", "wisdom", "charisma") for item in WIZARD_SPECIALIZATIONS)
    assert all(item.primary_weapon is None for item in WIZARD_SPECIALIZATIONS)
    assert tuple(item.spell_package_id for item in WIZARD_SPECIALIZATIONS) == (
        "evoker", "illusionist", "abjurer",
    )


def test_sorcerer_has_one_charisma_spell_specialization_per_target_subclass() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("sorcerer")) == (
        "draconic-sorcery", "aberrant-sorcery", "clockwork-sorcery",
    )
    assert all(item.ability_priority == ("charisma", "wisdom", "intelligence") for item in SORCERER_SPECIALIZATIONS)
    assert all(item.primary_weapon is None for item in SORCERER_SPECIALIZATIONS)
    assert tuple(item.spell_package_id for item in SORCERER_SPECIALIZATIONS) == (
        "draconic-sorcery", "aberrant-sorcery", "clockwork-sorcery",
    )
    assert SORCERER_SPECIALIZATIONS[0].feature_choice_ids == (
        "draconic-ancestor-red", "elemental-affinity-fire",
    )


def test_warlock_has_one_charisma_specialization_per_target_patron() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("warlock")) == (
        "fiend-patron", "great-old-one-patron", "celestial-patron",
    )
    fiend, great_old_one, celestial = WARLOCK_SPECIALIZATIONS
    assert (fiend.role, great_old_one.role, celestial.role) == (
        "eldritch-blaster", "control-caster", "weapon-caster-hybrid",
    )
    assert celestial.primary_weapon == "shortsword"
    assert celestial.feature_choice_ids == ("pact-of-the-blade",)
    assert all(item.ability_priority[0] == "charisma" for item in WARLOCK_SPECIALIZATIONS)


def test_bard_has_one_charisma_specialization_per_target_college() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("bard")) == (
        "college-lore", "college-valor", "college-glamour",
    )
    lore, valor, glamour = BARD_SPECIALIZATIONS
    assert (lore.role, valor.role, glamour.role) == (
        "support-healing", "weapon-caster-hybrid", "control-caster",
    )
    assert (valor.primary_weapon, valor.shield) == ("rapier", True)
    assert all(item.ability_priority[0] == "charisma" for item in BARD_SPECIALIZATIONS)


def test_cleric_has_one_wisdom_specialization_per_target_domain() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("cleric")) == (
        "life-domain", "light-domain", "war-domain",
    )
    life, light, war = CLERIC_SPECIALIZATIONS
    assert (life.role, life.primary_weapon, life.shield) == ("support-healing", "mace", True)
    assert (light.role, light.primary_weapon, light.shield) == ("radiant-control", None, False)
    assert (war.role, war.primary_weapon, war.shield) == ("frontline-support", "longsword", True)
    assert all(item.ability_priority[0] == "wisdom" for item in CLERIC_SPECIALIZATIONS)
    assert war.feature_choice_ids == ("blessed-strikes-divine-strike-radiant",)


def test_druid_has_one_wisdom_specialization_per_target_circle() -> None:
    assert tuple(item.subclass_id for item in specializations_for_class("druid")) == (
        "circle-land", "circle-moon", "circle-sea",
    )
    land, moon, sea = DRUID_SPECIALIZATIONS
    assert (land.role, land.spell_package_id) == ("fire-caster", "circle-land-arid")
    assert (moon.role, moon.spell_package_id) == ("wild-shape-melee", "circle-moon")
    assert (sea.role, sea.spell_package_id) == ("storm-controller", "circle-sea")
    assert all(item.ability_priority[0] == "wisdom" for item in DRUID_SPECIALIZATIONS)
    assert all((item.armor, item.primary_weapon, item.shield) == ("scale-mail", "scimitar", True)
               for item in DRUID_SPECIALIZATIONS)
    assert moon.feature_choice_ids == (
        "moon-beast-form-package", "elemental-fury-primal-strike-cold",
    )


def test_specialization_without_source_truth_fails_closed() -> None:
    with pytest.raises(ValueError, match="requires a source reference"):
        SubclassSpecialization(
            class_id="barbarian", subclass_id="invalid", subclass_name="Invalid",
            role="two-handed", ability_priority=("strength",), armor=None, shield=False,
            primary_weapon="greataxe", source_reference="",
        )
