"""Whole-clause 2014 Etherealness source audit over all 327 immutable cards."""
from __future__ import annotations

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_etherealness_2014 import (
    verified_unavailable_etherealness_2014,
)
from app.content.monster_supported_extra_actions_2014 import (
    source_supported_extra_action_labels_2014,
)

_EXPECTED = frozenset({"ghost", "night-hag", "succubus-incubus"})


def test_327_source_cards_prove_exactly_three_planar_only_actions() -> None:
    cards = load_monster_source_2014()
    assert len(cards) == 327
    found = {
        card.id
        for card in cards
        for name in card.action_names
        if verified_unavailable_etherealness_2014(card, name)
    }
    assert found == _EXPECTED
    for card in cards:
        if card.id in found:
            assert "Etherealness" in card.action_names
            assert "etherealness" in source_supported_extra_action_labels_2014(card)
            # An independently unsupported Action or trait must remain blocked.
            assert basic_blockers_2014(card)


def test_unknown_combat_riders_and_changed_plane_clauses_fail_closed() -> None:
    cards = {x.id: x for x in load_monster_source_2014()}
    for card_id in sorted(_EXPECTED):
        card = cards[card_id]
        original = card.model_dump_json()
        assert verified_unavailable_etherealness_2014(card, "Etherealness")
        source = card.source_actions
        assert source is not None
        altered = card.model_copy(update={
            "source_actions": source.replace(
                "Ethereal Plane from the Material Plane",
                "Astral Plane from the Material Plane",
            ),
        })
        assert not verified_unavailable_etherealness_2014(altered, "Etherealness")
        # A new save/damage rider cannot be silently discarded by its heading.
        altered = card.model_copy(update={
            "source_actions": source.replace(
                "</p>", " The next creature takes 2d6 force damage.</p>",
                1,
            ).replace(
                "or vice versa.", "or vice versa. Targets are stunned.", 1,
            ),
        })
        assert not verified_unavailable_etherealness_2014(altered, "Etherealness")
        renamed = card.model_copy(update={"id": "arbitrary-homebrew-creature", "name": "Renamed"})
        assert verified_unavailable_etherealness_2014(renamed, "Etherealness")
        assert card.model_dump_json() == original


def test_unproven_action_heading_not_silently_accepted() -> None:
    card = next(x for x in load_monster_source_2014() if x.id == "ghost")
    assert not verified_unavailable_etherealness_2014(card, "Horrifying Visage")
    assert not verified_unavailable_etherealness_2014(card, "Not A Real Action")

def test_prior_plane_shift_and_ethereal_stride_remain_excluded() -> None:
    # Do not re-enable another plane travel mechanism while classifying this
    # family; source identity is inspected only at the adapter boundary.
    from app.content.monster_arena_action_policy_2014 import (
        PIT_BANNED_ACTION_LABELS_2014, source_proven_ethereal_shift_action_2014,
    )

    assert "plane shift" in PIT_BANNED_ACTION_LABELS_2014
    source = {card.id: card for card in load_monster_source_2014()}
    nightmare = source["nightmare"]
    assert source_proven_ethereal_shift_action_2014(
        nightmare, "Ethereal Stride",
    )
    assert "ethereal stride" in source_supported_extra_action_labels_2014(nightmare)
    altered = nightmare.model_copy(update={
        "source_actions": nightmare.source_actions.replace(
            "or vice versa.",
            "or vice versa. All nearby creatures are stunned.",
        ),
    })
    assert not source_proven_ethereal_shift_action_2014(
        altered, "Ethereal Stride",
    )
