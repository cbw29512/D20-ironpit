"""Source-only classification of 2014 Gray Ooze Corrode Metal as arena-neutral.

Equipment durability and cumulative weapon penalties are not modeled in the Iron Pit.
Strict full-section match; any mutation fails closed. No name dispatch, no invented effects.
"""
import logging

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "gray-ooze")
    except Exception:
        logger.exception("Missing pinned Gray Ooze source.")
        raise


def test_corrode_metal_exact_source_is_arena_neutral():
    try:
        source = _source()
        original = source.model_dump_json()
        assert "Corrode Metal" in source.trait_names
        assert verified_arena_inert_trait_2014(source, "Corrode Metal")
        assert "Corrode Metal" not in unsupported_traits_2014(source)
        assert "source:trait" not in basic_blockers_2014(source)
        assert source.model_dump_json() == original
    except Exception:
        logger.exception("Gray Ooze Corrode Metal source proof failed.")
        raise


def test_corrode_metal_mutation_fails_closed():
    try:
        source = _source()
        mutations = (
            ("nonmagical weapon", "magical weapon"),
            ("cumulative -1 penalty", "cumulative -2 penalty"),
            ("destroyed", "and the wielder is poisoned"),
            ("2-inch-thick", "1-inch-thick"),
        )
        for before, after in mutations:
            changed = source.model_copy(
                update={"source_traits": source.source_traits.replace(before, after)}
            )
            assert changed.source_traits != source.source_traits
            assert not verified_arena_inert_trait_2014(changed, "Corrode Metal")
            assert "Corrode Metal" in unsupported_traits_2014(changed)
            assert "source:trait" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("Corrode Metal mutation was incorrectly accepted.")
        raise


def test_source_identity_is_not_a_runtime_dispatch_key():
    try:
        source = _source()
        renamed = source.model_copy(update={"id": "unrelated-ooze", "name": "Other Ooze"})
        assert verified_arena_inert_trait_2014(renamed, "Corrode Metal")
    except Exception:
        logger.exception("Neutral source proof incorrectly depended on a combatant ID/name.")
        raise
