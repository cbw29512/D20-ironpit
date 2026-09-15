from __future__ import annotations

from app.content.monster_catalog_2014_absorption import damage_absorptions_2014, unresolved_absorption_traits_2014


def test_absorption_parser_accepts_instead_and_plain_regains_wording() -> None:
    source = (
        "<strong>Acid Absorption.</strong> Whenever the golem is subjected to acid damage, "
        "it takes no damage and instead regains a number of hit points equal to the acid damage dealt. "
        "<strong>Lightning Absorption.</strong> Whenever the mound is subjected to lightning damage, "
        "it takes no damage and regains a number of hit points equal to the lightning damage dealt."
    )
    rules = damage_absorptions_2014(source)
    assert [rule.damage_type.value for rule in rules] == ["acid", "lightning"]


def test_absorption_trait_stays_blocked_without_matching_typed_rule() -> None:
    source = (
        "<strong>Fire Absorption.</strong> Whenever the golem is subjected to fire damage, "
        "it takes no damage and instead regains a number of hit points equal to the fire damage dealt."
    )
    assert unresolved_absorption_traits_2014(["Fire Absorption"], source) == []
    assert unresolved_absorption_traits_2014(["Lightning Absorption"], source) == ["Lightning Absorption"]
