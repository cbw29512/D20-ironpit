from app.content.bard_2014_spell_package import (
    additional_lore_magical_secrets_2014,
    build_bard_2014_spell_package,
)
from app.content.canonical_spell_policy import canonical_spell_package


def test_2014_bard_spell_package_matches_progression_counts() -> None:
    expected = {
        1: (2, 4),
        3: (2, 6),
        5: (3, 8),
        6: (3, 9),
        10: (4, 14),
        14: (4, 18),
        18: (4, 22),
        20: (4, 22),
    }
    for level, (cantrips, spells) in expected.items():
        package = build_bard_2014_spell_package(level)
        assert len(package.cantrips) == cantrips
        assert len(package.spells) == spells


def test_2014_bard_level_one_uses_legal_fully_supported_spell_choices() -> None:
    ids = {spell.id for spell in build_bard_2014_spell_package(1).spells}
    assert ids == {"healing-word", "cure-wounds", "detect-magic", "comprehend-languages"}


def test_lore_additional_magical_secrets_are_bonus_known_spells() -> None:
    assert additional_lore_magical_secrets_2014(5) == ()
    secrets = additional_lore_magical_secrets_2014(6)
    assert {spell.id for spell in secrets} == {"spiritual-weapon", "bless"}
    assert all("additional-magical-secrets" in spell.required_capabilities for spell in secrets)


def test_magical_secrets_count_inside_bard_spells_known() -> None:
    level_ten = build_bard_2014_spell_package(10)
    assert {"flame-strike", "death-ward"} <= {spell.id for spell in level_ten.spells}
    level_fourteen = build_bard_2014_spell_package(14)
    assert {"guiding-bolt", "shield-of-faith"} <= {spell.id for spell in level_fourteen.spells}
    level_eighteen = build_bard_2014_spell_package(18)
    assert {"aid", "inflict-wounds"} <= {spell.id for spell in level_eighteen.spells}


def test_canonical_policy_routes_2014_bard_to_edition_specific_package() -> None:
    package = canonical_spell_package("bard", 10, ruleset="2014")
    assert package is not None
    assert package.class_id == "bard"
    assert package.casting_ability == "charisma"
    assert len(package.spells) == 14
