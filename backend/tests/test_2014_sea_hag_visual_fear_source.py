"""Source-only regressions: these do not claim an executable Sea Hag."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_visual_fear_2014 import source_proven_visual_fear_2014


def _sea_hag():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "sea-hag")
    except Exception:
        raise AssertionError("Pinned 2014 Sea Hag source is missing") from None


def test_complete_pinned_horrific_appearance_source_is_extracted_without_mutation():
    try:
        monster = _sea_hag()
        snapshot = monster.model_dump_json()
        facts = source_proven_visual_fear_2014(monster)
        assert facts is not None
        assert (facts.source_name, facts.range_ft, facts.save_dc) == (
            "Horrific Appearance", 30, 11
        )
        assert facts.save_ability == "wisdom"
        assert facts.target_creature_types == ("humanoid",)
        assert facts.effect_id == "frightened"
        assert facts.duration_rounds == 10
        assert facts.repeat_save_timing == "target_turn_end"
        assert facts.repeat_save_disadvantage_while_source_visible
        assert facts.source_immunity_hours == 24
        assert facts.requires_true_form_visibility
        assert facts.aversion_attack_disadvantage_against_source
        assert facts.aversion_ends_at_next_turn
        assert facts.surprise_or_sudden_reveal_prevents_aversion
        assert monster.model_dump_json() == snapshot
        with pytest.raises(FrozenInstanceError):
            facts.save_dc = 99
    except Exception:
        raise


@pytest.mark.parametrize("old,new", [
    ("Any humanoid", "Any creature"),
    ("within 30 feet", "within 200 feet"),
    ("can see the hag's true form", "can hear the hag"),
    ("DC 11 Wisdom", "DC 15 Wisdom"),
    ("frightened for 1 minute", "frightened for 2 minutes"),
    ("at the end of each of its turns", "at the start of each of its turns"),
    ("with disadvantage if the hag is within line of sight", "without disadvantage"),
    ("on itself on a success", "on itself on a failure"),
    ("for the next 24 hours", "for the next 8 hours"),
    ("revelation of the hag's true form is sudden", "revelation is slow"),
    ("avert its eyes and avoid making the initial saving throw", "close its eyes"),
    ("has disadvantage on attack rolls against the hag", "has advantage on attacks"),
])
def test_source_changes_fail_closed_including_continuation(old, new):
    try:
        monster = _sea_hag()
        assert old in monster.source_traits
        changed = monster.model_copy(update={"source_traits": monster.source_traits.replace(old, new)})
        assert source_proven_visual_fear_2014(changed) is None
        assert source_proven_visual_fear_2014(monster) is not None
    except Exception:
        raise


def test_unrelated_named_trait_cannot_supply_missing_aversion_clause():
    try:
        monster = _sea_hag()
        first, continuation = monster.source_traits.rsplit("<p>", 1)
        spoofed = first + "<p><em><strong>Other Trait.</strong></em> " + continuation
        changed = monster.model_copy(update={"source_traits": spoofed})
        assert source_proven_visual_fear_2014(changed) is None
    except Exception:
        raise


def test_source_identity_is_display_only_and_unsupported_source_stays_blocked():
    try:
        monster = _sea_hag()
        renamed = monster.model_copy(update={"name": "Homebrew Facsimile", "id": "custom-visual-source"})
        assert source_proven_visual_fear_2014(renamed) == source_proven_visual_fear_2014(monster)
        unbound = monster.model_copy(update={"trait_names": ["Amphibious"]})
        assert source_proven_visual_fear_2014(unbound) is None
    except Exception:
        raise
