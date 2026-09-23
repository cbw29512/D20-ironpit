from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_qualified_defenses_2014 import (
    parse_qualified_defense_2014,
    qualified_damage_defenses_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.weapons import DamageType


def _monster(name: str):
    return next(monster for monster in load_monster_source_2014() if monster.name == name)


def test_gargoyle_qualified_resistance_binds_without_name_specific_logic() -> None:
    gargoyle = _monster("Gargoyle")
    rules = qualified_damage_defenses_2014(gargoyle)

    assert len(rules) == 1
    rule = rules[0]
    assert rule.kind == "resistance"
    assert rule.damage_types == [
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
        DamageType.SLASHING,
    ]
    assert rule.attack_only is True
    assert rule.magical is False
    assert rule.bypass_materials == ["adamantine"]
    assert basic_blockers_2014(gargoyle) == ()

    definition = adapt_basic_monster_2014(gargoyle)
    assert definition.qualified_damage_defenses == rules


def test_silvered_exception_uses_same_universal_parser() -> None:
    rule = parse_qualified_defense_2014(
        "Bludgeoning, Piercing, and Slashing from Nonmagical Attacks that aren't Silvered"
    )

    assert rule is not None
    assert rule.bypass_materials == ["silvered"]


def test_plain_nonmagical_resistance_uses_same_universal_parser() -> None:
    rule = parse_qualified_defense_2014(
        "Bludgeoning, Piercing, and Slashing from Nonmagical Attacks"
    )

    assert rule is not None
    assert rule.bypass_materials == []


def test_alignment_specific_rakshasa_clause_remains_fail_closed() -> None:
    assert parse_qualified_defense_2014(
        "Piercing from Magic Weapons Wielded by Good Creatures"
    ) is None
