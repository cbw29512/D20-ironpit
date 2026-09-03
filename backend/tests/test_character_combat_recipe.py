import pytest

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.character_combat_recipe import compose_character_combat_recipe


def test_champion_recipe_is_only_the_two_handed_specialization() -> None:
    champion = compose_character_combat_recipe("fighter", "champion", "great-weapon", 8)
    expected = canonical_combat_features("fighter", 8, "champion")

    assert champion.shared_progression_id == "fighter-1-20"
    assert champion.combat_features == expected
    assert champion.build_status == "planned"
    assert champion.build_choices is not None
    assert champion.build_choices.fighting_style == "Great Weapon Fighting"
    assert champion.build_choices.primary_weapon == "greatsword"
    assert champion.build_choices.weapon_masteries[0] == "greatsword"


def test_old_champion_weapon_clones_are_rejected_by_subclass_contract() -> None:
    expected = {
        "sword-shield": "eldritch-knight",
        "archer": "psi-warrior",
        "dual-wield": "battle-master",
    }
    for build_id, required_subclass in expected.items():
        with pytest.raises(ValueError, match=f"requires subclass {required_subclass}"):
            compose_character_combat_recipe("fighter", "champion", build_id, 8)


def test_new_fighter_subclasses_compose_from_one_class_spine_but_stay_planned() -> None:
    expected_features = {
        "battle-master": "battle-master-know-your-enemy",
        "eldritch-knight": "eldritch-knight-war-magic",
        "psi-warrior": "psi-warrior-telekinetic-adept",
    }
    for subclass_id, build_id in (
        ("battle-master", "dual-wield"),
        ("eldritch-knight", "sword-shield"),
        ("psi-warrior", "archer"),
    ):
        recipe = compose_character_combat_recipe("fighter", subclass_id, build_id, 8)
        assert recipe.shared_progression_id == "fighter-1-20"
        assert recipe.build_status == "planned"
        assert expected_features[subclass_id] in recipe.combat_features
        assert recipe.build_choices is not None


def test_fighter_subclass_specializations_keep_their_declared_weapons() -> None:
    battle_master = compose_character_combat_recipe("fighter", "battle-master", "dual-wield", 8)
    eldritch_knight = compose_character_combat_recipe("fighter", "eldritch-knight", "sword-shield", 8)
    psi = compose_character_combat_recipe("fighter", "psi-warrior", "archer", 8)
    assert battle_master.build_choices.primary_weapon == "shortsword"
    assert battle_master.build_choices.secondary_weapons[0] == "scimitar"
    assert eldritch_knight.build_choices.primary_weapon == "longsword"
    assert eldritch_knight.build_choices.shield is True
    assert psi.build_choices.primary_weapon == "longbow"


def test_barbarian_subclasses_compose_real_planned_loadouts_from_one_spine() -> None:
    expected = {
        ("path-berserker", "great-weapon"): ("greataxe", False),
        ("path-wild-heart", "weapon-shield"): ("battleaxe", True),
        ("path-zealot", "dual-wield"): ("shortsword", False),
    }
    for (subclass_id, build_id), (weapon_id, shield) in expected.items():
        recipe = compose_character_combat_recipe("barbarian", subclass_id, build_id, 8)
        assert recipe.shared_progression_id == "barbarian-1-20"
        assert recipe.build_status == "planned"
        assert recipe.build_choices.primary_weapon == weapon_id
        assert recipe.build_choices.shield is shield


def test_monk_subclasses_compose_real_planned_roles_from_one_spine() -> None:
    expected = {
        ("warrior-open-hand", "unarmed-offense"): None,
        ("warrior-shadow", "weapon-monk"): "shortsword",
        ("warrior-elements", "defensive-mobile"): None,
    }
    for (subclass_id, build_id), weapon_id in expected.items():
        recipe = compose_character_combat_recipe("monk", subclass_id, build_id, 11)
        assert recipe.shared_progression_id == "monk-1-20"
        assert recipe.build_status == "planned"
        assert recipe.build_choices.primary_weapon == weapon_id
        assert not recipe.build_choices.weapon_masteries


def test_paladin_oaths_compose_real_planned_loadouts_from_one_spine() -> None:
    expected = {
        ("oath-devotion", "sword-shield"): ("longsword", True),
        ("oath-vengeance", "great-weapon"): ("greatsword", False),
        ("oath-ancients", "support-healer"): ("battleaxe", True),
    }
    for (subclass_id, build_id), (weapon_id, shield) in expected.items():
        recipe = compose_character_combat_recipe("paladin", subclass_id, build_id, 15)
        assert recipe.shared_progression_id == "paladin-1-20"
        assert recipe.build_status == "planned"
        assert recipe.build_choices.primary_weapon == weapon_id
        assert recipe.build_choices.shield is shield
        assert "aura-of-protection" in recipe.combat_features


def test_ranger_subclasses_compose_real_planned_loadouts_from_one_spine() -> None:
    expected = {
        ("hunter", "sword-shield"): ("shortsword", True),
        ("gloom-stalker", "archer"): ("longbow", False),
        ("beastmaster", "dual-wield"): ("shortsword", False),
    }
    for (subclass_id, build_id), (weapon_id, shield) in expected.items():
        recipe = compose_character_combat_recipe("ranger", subclass_id, build_id, 15)
        assert recipe.shared_progression_id == "ranger-1-20"
        assert recipe.build_status == "planned"
        assert recipe.build_choices.primary_weapon == weapon_id
        assert recipe.build_choices.shield is shield
        assert "extra-attack" in recipe.combat_features


def test_rogue_subclasses_compose_real_planned_loadouts_from_one_spine() -> None:
    expected = {
        ("thief", "dual-wield"): "shortsword",
        ("assassin", "ranged"): "shortbow",
        ("arcane-trickster", "duelist"): "rapier",
    }
    for (subclass_id, build_id), weapon_id in expected.items():
        recipe = compose_character_combat_recipe("rogue", subclass_id, build_id, 17)
        assert recipe.shared_progression_id == "rogue-1-20"
        assert recipe.build_status == "planned"
        assert recipe.build_choices.primary_weapon == weapon_id
        assert "sneak-attack" in recipe.combat_features


def test_wizard_subclasses_compose_real_planned_spell_packages_from_one_spine() -> None:
    expected = {
        ("evoker", "fire-damage"): "evoker",
        ("illusionist", "frost-control"): "illusionist",
        ("abjurer", "mixed-arcane"): "abjurer",
    }
    for (subclass_id, build_id), spell_package_id in expected.items():
        recipe = compose_character_combat_recipe("wizard", subclass_id, build_id, 14)
        assert recipe.shared_progression_id == "wizard-1-20"
        assert recipe.build_status == "planned"
        assert recipe.build_choices.spell_package_id == spell_package_id
        assert "wizard-spellcasting" in recipe.combat_features


def test_sorcerer_subclasses_compose_real_planned_spell_packages_from_one_spine() -> None:
    expected = {
        ("draconic-sorcery", "fire-damage"): "draconic-sorcery",
        ("aberrant-sorcery", "frost-control"): "aberrant-sorcery",
        ("clockwork-sorcery", "mixed-arcane"): "clockwork-sorcery",
    }
    for (subclass_id, build_id), spell_package_id in expected.items():
        recipe = compose_character_combat_recipe("sorcerer", subclass_id, build_id, 18)
        assert recipe.shared_progression_id == "sorcerer-1-20"
        assert recipe.build_status == "planned"
        assert recipe.build_choices.spell_package_id == spell_package_id
        assert "sorcerer-spellcasting" in recipe.combat_features


def test_subclass_specific_build_fails_closed_on_the_wrong_subclass() -> None:
    with pytest.raises(ValueError, match="requires subclass circle-moon"):
        compose_character_combat_recipe("druid", "circle-land", "moon-melee", 3)


def test_build_cannot_be_borrowed_by_another_class() -> None:
    with pytest.raises(ValueError, match="Unknown paladin combat build variant"):
        compose_character_combat_recipe("paladin", "oath-devotion", "archer", 3)
