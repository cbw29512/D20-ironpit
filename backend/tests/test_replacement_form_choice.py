from __future__ import annotations

import pytest

from app.combat.replacement_form_choice import (
    FormMatchupProjection,
    choose_profitable_change_shape,
    choose_profitable_replacement_form,
)


def _form(
    ident: str,
    outgoing: float,
    incoming: float,
    control: float = 0.0,
    legal: bool = True,
) -> FormMatchupProjection:
    return FormMatchupProjection(ident, outgoing, incoming, control, legal)


def test_low_turn_budget_or_weak_form_stays_deva() -> None:
    deva = _form("2014-deva", 30, 15)
    ape = _form("2014-giant-ape", 40, 16)
    assert choose_profitable_change_shape(
        deva, [ape], expected_future_turns=1, change_shape_action_cost=30,
    ) is None
    assert choose_profitable_change_shape(
        deva, [ape], expected_future_turns=4, change_shape_action_cost=40,
    ) is None


def test_multiple_matchups_select_the_genuinely_profitable_legal_form() -> None:
    deva = _form("2014-deva", 30, 15)
    scorpion = _form("2014-giant-scorpion", 45, 20, control=6)
    ape = _form("2014-giant-ape", 47, 18)
    rex = _form("2014-tyrannosaurus-rex", 44, 17, control=9)
    assert choose_profitable_change_shape(
        deva, [scorpion, ape, rex], expected_future_turns=4,
        change_shape_action_cost=30,
    ) == "2014-tyrannosaurus-rex"
    assert choose_profitable_change_shape(
        deva, [_form("uncertified", 200, 0, legal=False), ape],
        expected_future_turns=4, change_shape_action_cost=30,
    ) == "2014-giant-ape"


def test_zero_future_turns_and_bad_projections_are_rejected() -> None:
    deva = _form("2014-deva", 30, 10)
    assert choose_profitable_change_shape(
        deva, [_form("2014-giant-ape", 99, 0)],
        expected_future_turns=0, change_shape_action_cost=30,
    ) is None
    with pytest.raises(ValueError, match="duplicate"):
        choose_profitable_change_shape(
            deva, [_form("x", 40, 10), _form("x", 40, 10)],
            expected_future_turns=3, change_shape_action_cost=30,
        )
    with pytest.raises(ValueError, match="nonnegative"):
        choose_profitable_change_shape(
            deva, [_form("x", 40, 10)],
            expected_future_turns=-1, change_shape_action_cost=30,
        )
    with pytest.raises(ValueError, match="finite"):
        choose_profitable_change_shape(
            deva, [_form("x", float("nan"), 10)],
            expected_future_turns=3, change_shape_action_cost=30,
        )


def test_counter_form_is_chosen_for_likely_status_loss_not_raw_cr() -> None:
    baseline = FormMatchupProjection(
        "2014-deva", 30, 15, incoming_condition_cost_per_round=12,
    )
    resistant = FormMatchupProjection(
        "2014-resistant-humanoid", 27, 11, incoming_condition_cost_per_round=0,
    )
    stronger_but_vulnerable = FormMatchupProjection(
        "2014-strong-beast", 39, 18, incoming_condition_cost_per_round=12,
    )
    assert choose_profitable_change_shape(
        baseline, [resistant, stronger_but_vulnerable],
        expected_future_turns=4, change_shape_action_cost=20,
    ) == "2014-resistant-humanoid"
    # If its immunity would not apply to the enemy's printed effects, no
    # fictitious condition avoidance is projected and it stays a Deva.
    no_counter = FormMatchupProjection(
        "2014-resistant-humanoid", 27, 11, incoming_condition_cost_per_round=12,
    )
    assert choose_profitable_change_shape(
        baseline, [no_counter],
        expected_future_turns=3, change_shape_action_cost=20,
    ) is None


def test_same_engine_selector_accepts_edition_owned_wild_shape_costs() -> None:
    """2014 Action / 2024 Bonus Action affect decisions; legal forms remain external."""
    for edition in ("2014", "2024"):
        current = _form(f"{edition}-druid", outgoing=15, incoming=10)
        beast = _form(f"{edition}-wolf", outgoing=23, incoming=10)
        # Identical source-derived combat matchup; changing as an Action costs
        # more of this turn than changing as a Bonus Action. Both editions pass
        # explicit transformation costs; no DRUID-name dispatch in the chooser.
        action_cost = 20 if edition == "2014" else 5
        selection = choose_profitable_replacement_form(
            current, [beast],
            expected_future_turns=2,
            transformation_opportunity_cost=action_cost,
        )
        assert selection == (None if edition == "2014" else f"{edition}-wolf")


def test_generic_form_selector_refuses_uncompiled_source_options() -> None:
    current = _form("2014-druid", 15, 10)
    unknown_form = _form("2014-uncertified-beast", 100, 0, legal=False)
    assert choose_profitable_replacement_form(
        current, [unknown_form],
        expected_future_turns=10,
        transformation_opportunity_cost=5,
    ) is None
