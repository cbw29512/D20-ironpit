from app.content.paladin_2014_spell_package import build_paladin_2014_spell_package


def test_level_twelve_paladin_has_complete_ten_spell_prepared_package() -> None:
    package = build_paladin_2014_spell_package(12, 4)
    assert package is not None
    assert len(package.spells) == 10
    assert [spell.id for spell in package.spells[-2:]] == [
        "locate-object",
        "create-food-and-water",
    ]
    assert all(spell.spell_level <= 3 for spell in package.spells)
