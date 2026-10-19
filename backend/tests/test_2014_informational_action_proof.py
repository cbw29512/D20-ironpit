"""Information-only Actions are source-visible and cannot fake combat effects."""
from __future__ import annotations

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_informational_action_proofs_2014 import verified_nonactionable_action_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _sprite():
    return next(row for row in load_monster_source_2014() if row.id == "sprite")


def _without_unimplemented_invisibility(sprite):
    # Proof variant only: the real card keeps Invisibility and stays blocked.
    source = sprite.source_actions
    assert source is not None and "<strong>Invisibility.</strong>" in source
    return sprite.model_copy(update={
        "action_names": [name for name in sprite.action_names if name != "Invisibility"],
        "source_actions": source.split("<p><em><strong>Invisibility.</strong>")[0],
    })


def test_heart_sight_is_source_verified_neutral_without_dropping_original_action() -> None:
    sprite = _sprite()
    before = sprite.model_dump_json()
    assert verified_nonactionable_action_2014(sprite, "Heart Sight")
    assert not verified_nonactionable_action_2014(sprite, "Invisibility")
    assert "Heart Sight" in sprite.action_names
    assert "current emotional state" in (sprite.source_actions or "")
    assert basic_blockers_2014(sprite) == ("source:extra-action",)
    assert sprite.model_dump_json() == before


def test_verified_information_action_clears_only_its_own_source_blocker() -> None:
    variant = _without_unimplemented_invisibility(_sprite())
    assert verified_nonactionable_action_2014(variant, "Heart Sight")
    assert "source:extra-action" not in basic_blockers_2014(variant)


def test_mismatched_printed_source_fails_closed_instead_of_using_action_name() -> None:
    neutral_variant = _without_unimplemented_invisibility(_sprite())
    original = neutral_variant.source_actions
    assert original is not None
    for altered in (
        original.replace("DC 10 Charisma", "DC 11 Charisma"),
        original.replace("current emotional state", "armor class"),
        original.replace(
            "undead automatically fail the saving throw.",
            "undead automatically fail the saving throw. The sprite gains Advantage on attacks.",
        ),
    ):
        mutant = neutral_variant.model_copy(update={"source_actions": altered})
        assert not verified_nonactionable_action_2014(mutant, "Heart Sight")
        assert "source:extra-action" in basic_blockers_2014(mutant)


def test_unknown_or_missing_source_action_is_not_exempt() -> None:
    sprite = _sprite()
    assert not verified_nonactionable_action_2014(sprite, "Wail (1/Day)")
    no_heading = sprite.model_copy(update={
        "source_actions": (sprite.source_actions or "").replace("<strong>Heart Sight.</strong>", "<strong>Other.</strong>")
    })
    assert not verified_nonactionable_action_2014(no_heading, "Heart Sight")
