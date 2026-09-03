import pytest

from app.content.class_spell_progression import max_spell_level
from app.content.wizard_combat_levels import WIZARD_COMBAT_LEVELS
from app.content.wizard_subclass_spell_package_data import (
    WIZARD_SUBCLASS_SPELL_PACKAGES,
    wizard_specialization_spells,
)


def test_each_wizard_specialization_has_a_complete_legal_prepared_package() -> None:
    assert set(WIZARD_SUBCLASS_SPELL_PACKAGES) == {"evoker", "illusionist", "abjurer"}
    for subclass_id, package in WIZARD_SUBCLASS_SPELL_PACKAGES.items():
        assert len({spell_id for _, _, spell_id in package}) == len(package)
        for level in range(1, 21):
            active = [(spell_level, spell_id) for unlock, spell_level, spell_id in package if unlock <= level]
            assert len(active) == WIZARD_COMBAT_LEVELS[level].prepared_spells
            assert all(spell_level <= max_spell_level("wizard", level) for spell_level, _ in active)
            assert wizard_specialization_spells(subclass_id, level) == tuple(
                spell_id for _, spell_id in active
            )


def test_unknown_or_invalid_wizard_spell_package_requests_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unknown Wizard spell specialization"):
        wizard_specialization_spells("not-a-subclass", 1)
    with pytest.raises(ValueError, match="between 1 and 20"):
        wizard_specialization_spells("evoker", 0)
