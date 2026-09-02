import pytest

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.character_combat_recipe import compose_character_combat_recipe


def test_build_recipe_reuses_one_class_and_subclass_feature_progression() -> None:
    great_weapon = compose_character_combat_recipe("fighter", "champion", "great-weapon", 8)
    archer = compose_character_combat_recipe("fighter", "champion", "archer", 8)
    expected = canonical_combat_features("fighter", 8, "champion")

    assert great_weapon.shared_progression_id == "fighter-1-20"
    assert archer.shared_progression_id == "fighter-1-20"
    assert great_weapon.combat_features == expected
    assert archer.combat_features == expected
    assert great_weapon.build_id != archer.build_id
    assert great_weapon.role != archer.role
    assert archer.build_status == "planned"


def test_fighter_recipe_composes_the_role_choice_overlay_too() -> None:
    archer = compose_character_combat_recipe("fighter", "champion", "archer", 8)
    dual = compose_character_combat_recipe("fighter", "champion", "dual-wield", 8)

    assert archer.build_choices is not None
    assert archer.build_choices.primary_weapon == "longbow"
    assert archer.build_choices.fighting_style == "Archery"
    assert dual.build_choices is not None
    assert dual.build_choices.weapon_masteries[:2] == ("scimitar", "shortsword")
    assert "nick-mastery" in dual.build_choices.required_capabilities


def test_rogue_base_and_thief_overlay_are_independent_of_build_role() -> None:
    duelist = compose_character_combat_recipe("rogue", "thief", "duelist", 3)
    ranged = compose_character_combat_recipe("rogue", "thief", "ranged", 3)
    assert duelist.combat_features == ranged.combat_features
    assert "sneak-attack" in duelist.combat_features
    assert "thief-fast-hands" in duelist.combat_features
    assert duelist.build_choices is None
    assert ranged.build_choices is None


def test_subclass_specific_build_fails_closed_on_the_wrong_subclass() -> None:
    with pytest.raises(ValueError, match="requires subclass circle-moon"):
        compose_character_combat_recipe("druid", "circle-land", "moon-melee", 3)


def test_build_cannot_be_borrowed_by_another_class() -> None:
    with pytest.raises(ValueError, match="Unknown paladin combat build variant"):
        compose_character_combat_recipe("paladin", "oath-devotion", "archer", 3)
