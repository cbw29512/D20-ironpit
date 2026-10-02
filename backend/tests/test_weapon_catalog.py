import pytest

from app.content.weapon_catalog import audited_weapon_ids, build_weapon


def test_audited_weapon_catalog_preserves_shared_properties_and_masteries() -> None:
    greataxe = build_weapon("greataxe")
    battleaxe = build_weapon("battleaxe")
    greatsword = build_weapon("greatsword")
    longsword = build_weapon("longsword")
    mace = build_weapon("mace")
    sickle = build_weapon("sickle")
    dagger = build_weapon("dagger")
    scimitar = build_weapon("scimitar")
    shortsword = build_weapon("shortsword")
    rapier = build_weapon("rapier")
    handaxe = build_weapon("handaxe")
    javelin = build_weapon("javelin")
    longbow = build_weapon("longbow")
    shortbow = build_weapon("shortbow")

    assert (greataxe.mastery_property, greataxe.heavy, greataxe.two_handed) == ("Cleave", True, True)
    assert (battleaxe.mastery_property, battleaxe.versatile) == ("Topple", True)
    assert (greatsword.mastery_property, greatsword.heavy, greatsword.two_handed) == ("Graze", True, True)
    assert (longsword.mastery_property, longsword.versatile) == ("Sap", True)
    assert mace.mastery_property == "Sap"
    assert (sickle.mastery_property, sickle.finesse, sickle.light, sickle.dice_size) == ("Nick", False, True, 4)
    assert (dagger.mastery_property, dagger.finesse, dagger.light, dagger.dice_size) == ("Nick", True, True, 4)
    assert (scimitar.mastery_property, scimitar.finesse, scimitar.light) == ("Nick", True, True)
    assert (shortsword.mastery_property, shortsword.finesse, shortsword.light) == ("Vex", True, True)
    assert (rapier.mastery_property, rapier.finesse, rapier.light) == ("Vex", True, False)
    assert (handaxe.mastery_property, handaxe.light) == ("Vex", True)
    assert (handaxe.normal_range_ft, handaxe.long_range_ft, handaxe.projectile) == (20, 60, "handaxe")
    assert (javelin.mastery_property, javelin.dice_size, javelin.damage_type.value) == ("Slow", 6, "piercing")
    assert (javelin.normal_range_ft, javelin.long_range_ft, javelin.projectile) == (30, 120, "javelin")
    assert (longbow.mastery_property, longbow.heavy, longbow.two_handed) == ("Slow", True, True)
    assert (shortbow.mastery_property, shortbow.two_handed) == ("Vex", True)
    assert audited_weapon_ids() == (
        "greataxe", "battleaxe", "greatsword", "longsword", "mace", "sickle", "dagger", "scimitar", "shortsword",
        "rapier", "handaxe", "javelin", "longbow", "shortbow",
    )


def test_weapon_catalog_returns_independent_records() -> None:
    first = build_weapon("scimitar")
    second = build_weapon("scimitar")
    first.name = "Changed"
    assert second.name == "Scimitar"


def test_unknown_weapon_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown audited weapon"):
        build_weapon("not-a-weapon")
