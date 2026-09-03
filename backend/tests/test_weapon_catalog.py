import pytest

from app.content.weapon_catalog import audited_weapon_ids, build_weapon


def test_audited_weapon_catalog_preserves_shared_properties_and_masteries() -> None:
    greataxe = build_weapon("greataxe")
    battleaxe = build_weapon("battleaxe")
    greatsword = build_weapon("greatsword")
    longsword = build_weapon("longsword")
    mace = build_weapon("mace")
    scimitar = build_weapon("scimitar")
    shortsword = build_weapon("shortsword")
    rapier = build_weapon("rapier")
    longbow = build_weapon("longbow")
    shortbow = build_weapon("shortbow")

    assert (greataxe.mastery_property, greataxe.heavy, greataxe.two_handed) == ("Cleave", True, True)
    assert (battleaxe.mastery_property, battleaxe.versatile) == ("Topple", True)
    assert (greatsword.mastery_property, greatsword.heavy, greatsword.two_handed) == ("Graze", True, True)
    assert (longsword.mastery_property, longsword.versatile) == ("Sap", True)
    assert mace.mastery_property == "Sap"
    assert (scimitar.mastery_property, scimitar.finesse, scimitar.light) == ("Nick", True, True)
    assert (shortsword.mastery_property, shortsword.finesse, shortsword.light) == ("Vex", True, True)
    assert (rapier.mastery_property, rapier.finesse, rapier.light) == ("Vex", True, False)
    assert (longbow.mastery_property, longbow.heavy, longbow.two_handed) == ("Slow", True, True)
    assert (shortbow.mastery_property, shortbow.two_handed) == ("Vex", True)
    assert audited_weapon_ids() == (
        "greataxe", "battleaxe", "greatsword", "longsword", "mace", "scimitar", "shortsword",
        "rapier", "longbow", "shortbow",
    )


def test_weapon_catalog_returns_independent_records() -> None:
    first = build_weapon("scimitar")
    second = build_weapon("scimitar")
    first.name = "Changed"
    assert second.name == "Scimitar"


def test_unknown_weapon_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unknown audited weapon"):
        build_weapon("not-a-weapon")
