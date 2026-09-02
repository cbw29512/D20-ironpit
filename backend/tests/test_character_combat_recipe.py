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


def test_new_fighter_subclasses_remain_fail_closed_until_their_feature_overlays_are_audited() -> None:
    for subclass_id, build_id in (
        ("battle-master", "dual-wield"),
        ("eldritch-knight", "sword-shield"),
        ("psi-warrior", "archer"),
    ):
        with pytest.raises(ValueError, match="Unknown combat subclass overlay"):
            compose_character_combat_recipe("fighter", subclass_id, build_id, 8)


def test_rogue_base_and_thief_overlay_are_independent_of_legacy_role_record() -> None:
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
