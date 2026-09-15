from app.content.monster_catalog_2014_defenses import conditional_resistances_2014
from app.domain.weapons import DamageType


def test_full_physical_adamantine_resistance_still_parses() -> None:
    rules = conditional_resistances_2014(
        "bludgeoning, piercing, and slashing from nonmagical attacks that aren't adamantine"
    )

    assert len(rules) == 1
    assert rules[0].damage_types == [
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
        DamageType.SLASHING,
    ]
    assert rules[0].nonmagical_attack_only is True
    assert rules[0].bypass_if_adamantine is True


def test_xorn_physical_subset_parses_without_inventing_bludgeoning() -> None:
    rules = conditional_resistances_2014(
        "piercing and slashing from nonmagical attacks that aren't adamantine"
    )

    assert len(rules) == 1
    assert rules[0].damage_types == [DamageType.PIERCING, DamageType.SLASHING]
    assert rules[0].nonmagical_attack_only is True
    assert rules[0].bypass_if_adamantine is True
    assert rules[0].bypass_if_silvered is False


def test_unknown_nonmagical_qualifier_fails_closed() -> None:
    rules = conditional_resistances_2014(
        "piercing and slashing from nonmagical attacks that aren't mithral"
    )

    assert rules == []
