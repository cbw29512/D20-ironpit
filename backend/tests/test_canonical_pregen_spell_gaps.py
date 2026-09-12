from app.content.canonical_pregen_spell_gaps import (
    canonical_pregen_spell_package_gaps,
    first_spell_package_gap_by_class,
)
from app.content.canonical_spell_packages import CANONICAL_SPELLS


def test_spell_gap_audit_covers_every_canonical_caster() -> None:
    first = first_spell_package_gap_by_class()

    assert set(first) == set(CANONICAL_SPELLS)
    assert first["cleric"] is not None
    assert first["cleric"].level == 5


def test_spell_gap_rows_are_deterministic_and_actionable() -> None:
    gaps = canonical_pregen_spell_package_gaps()
    keys = [(gap.class_id, gap.level) for gap in gaps]

    assert keys == sorted(keys)
    assert len(keys) == len(set(keys))
    assert all(gap.reason for gap in gaps)
    assert ("cleric", 5) in keys
