from app.content.monster_catalog_2014_defenses import conditional_resistances_2014, unresolved_defenses_2014


def test_weapon_qualified_defenses_are_ignored_in_iron_pit() -> None:
    clauses = [
        "piercing from magic weapons wielded by good creatures",
        "piercing and slashing from nonmagical attacks that aren't adamantine",
        "bludgeoning, piercing, and slashing from nonmagical attacks that aren't silvered",
        "bludgeoning, piercing, and slashing from nonmagical attacks",
    ]

    assert conditional_resistances_2014(clauses) == []
    assert unresolved_defenses_2014(clauses) == []


def test_non_weapon_defense_text_still_fails_closed() -> None:
    assert unresolved_defenses_2014(["fire damage from spells cast by dragons"]) == [
        "fire damage from spells cast by dragons"
    ]
