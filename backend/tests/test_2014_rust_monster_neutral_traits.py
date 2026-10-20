"""Approved source policies remove traits only; Antennae remains fail-closed."""
import logging

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_save_capabilities_2014 import unsupported_source_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def _source(monster_id="rust-monster"):
    try:
        return next(row for row in load_monster_source_2014() if row.id == monster_id)
    except Exception:
        logger.exception("Missing pinned source for neutral-trait test: %s.", monster_id)
        raise


def test_approved_traits_are_preserved_without_admitting_antennae():
    try:
        source = _source()
        original = source.model_dump_json()
        assert verified_arena_inert_trait_2014(source, "Iron Scent")
        assert verified_arena_inert_trait_2014(source, "Rust Metal")
        assert unsupported_traits_2014(source) == ()
        assert basic_blockers_2014(source) == ("source:extra-action",)
        assert unsupported_source_actions_2014(source) == ["Antennae"]
        assert source.attacks[0].name == "Bite" and source.attacks[0].damage.bonus == 1
        assert source.model_dump_json() == original
    except Exception:
        logger.exception("Approved Rust Monster source policy changed its card or admitted Antennae.")
        raise


def test_unknown_effects_and_changed_range_stay_blocked():
    try:
        source = _source()
        for name, before, after in (
            ("Iron Scent", "within 30 feet", "within 60 feet"),
            ("Iron Scent", "within 30 feet of it.", "within 30 feet of it. Enemies take 1d6 fire damage."),
            ("Rust Metal", "nonmagical weapon", "magical weapon"),
            ("Rust Metal", "penalty to damage rolls", "penalty to attack rolls"),
            ("Rust Metal", "destroyed after dealing damage.", "destroyed after dealing damage and the wielder is poisoned."),
        ):
            changed = source.model_copy(update={"source_traits": source.source_traits.replace(before, after)})
            assert changed.source_traits != source.source_traits
            assert not verified_arena_inert_trait_2014(changed, name)
            assert name in unsupported_traits_2014(changed)
            assert "source:trait" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("Unapproved source mutation inherited a neutral trait classification.")
        raise


def test_unheaded_continuation_cannot_hide_a_combat_rider():
    try:
        source = _source()
        changed = source.model_copy(update={"source_traits": source.source_traits + "<p>Enemies take 1d6 acid damage.</p>"})
        # Ordinary callers retain their existing one-paragraph source view.
        ordinary = source_sections_2014(changed.source_traits)["Rust Metal"]
        complete = source_sections_2014(changed.source_traits, include_continuations=True)["Rust Metal"]
        assert "Enemies take" not in ordinary and "Enemies take" in complete
        assert not verified_arena_inert_trait_2014(changed, "Rust Metal")
        assert "source:trait" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("A continuation paragraph bypassed complete source proof.")
        raise


def test_missing_source_and_unrelated_gray_ooze_remain_blocked():
    try:
        source = _source()
        for changed in (
            source.model_copy(update={"source_traits": None}),
            source.model_copy(update={"trait_names": []}),
        ):
            for name in ("Iron Scent", "Rust Metal"):
                assert not verified_arena_inert_trait_2014(changed, name)
        gray_ooze = _source("gray-ooze")
        assert not verified_arena_inert_trait_2014(gray_ooze, "Corrode Metal")
        assert "Corrode Metal" in unsupported_traits_2014(gray_ooze)
    except Exception:
        logger.exception("A missing or unrelated source was classified under another trait's policy.")
        raise


def test_source_identity_is_not_a_runtime_dispatch_key():
    try:
        renamed = _source().model_copy(update={"id": "unrelated-source", "name": "Other Creature"})
        for name in ("Iron Scent", "Rust Metal"):
            assert verified_arena_inert_trait_2014(renamed, name)
        assert basic_blockers_2014(renamed) == ("source:extra-action",)
    except Exception:
        logger.exception("Neutral source proof incorrectly depended on a combatant ID/name.")
        raise
