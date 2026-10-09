from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


@dataclass(frozen=True)
class FormMatchupProjection:
    """Source-derived estimate *after* the engine validates all legal form abilities.

    Attack accuracy, defenses, opposing damage types, mobility, senses, and
    status effects must be valued by existing universal combat primitives,
    including expected incoming incapacitation/debuff costs AFTER own immunity,
    qualifying saving-throw defenses, and spell Magic Resistance,
    not by a monster-name branch or an arbitrary source CR multiplier.
    """
    form_template_id: str
    outgoing_damage_per_round: float
    incoming_damage_per_round: float
    control_value_per_round: float = 0.0
    legally_compiled: bool = True
    incoming_condition_cost_per_round: float = 0.0


def choose_profitable_change_shape(
    current: FormMatchupProjection,
    candidates: Iterable[FormMatchupProjection],
    *,
    expected_future_turns: int,
    change_shape_action_cost: float,
) -> str | None:
    """Choose a form only when its projected future advantage repays changing.

    This pure selector is NOT wired to the 2014 Deva's AI until complete form
    attacks, source action legality, and matchup projections are certified.
    Ineligible forms and tied/nonpositive improvements always leave the
    actor unchanged. No form-switching loop is introduced here.
    """
    if isinstance(expected_future_turns, bool) or not isinstance(expected_future_turns, int) or expected_future_turns < 0:
        raise ValueError("Future turn estimate must be nonnegative.")
    if change_shape_action_cost < 0 or not isfinite(change_shape_action_cost):
        raise ValueError("Change Shape Action opportunity cost must be finite and nonnegative.")
    if not current.legally_compiled or not current.form_template_id:
        raise ValueError("Baseline form must be source-validated.")

    def validate(row: FormMatchupProjection) -> None:
        if not row.form_template_id:
            raise ValueError("Every candidate requires a source template ID.")
        if not all(isfinite(item) and item >= 0 for item in (
            row.outgoing_damage_per_round, row.incoming_damage_per_round,
            row.control_value_per_round, row.incoming_condition_cost_per_round,
        )):
            raise ValueError("Projected source combat values must be finite and nonnegative.")

    validate(current)
    best_score = 0.0
    best_id: str | None = None
    seen: set[str] = set()
    for row in candidates:
        validate(row)
        if row.form_template_id in seen or row.form_template_id == current.form_template_id:
            raise ValueError("Change Shape shortlist contains a duplicate or baseline form.")
        seen.add(row.form_template_id)
        if not row.legally_compiled:
            continue
        advantage_per_round = (
            (row.outgoing_damage_per_round - current.outgoing_damage_per_round)
            + (current.incoming_damage_per_round - row.incoming_damage_per_round)
            + row.control_value_per_round - current.control_value_per_round
            + current.incoming_condition_cost_per_round - row.incoming_condition_cost_per_round
        )
        score = advantage_per_round * expected_future_turns - change_shape_action_cost
        if score > best_score or (score == best_score and best_id is not None and row.form_template_id < best_id):
            best_score = score
            best_id = row.form_template_id
    return best_id


def choose_profitable_replacement_form(
    current: FormMatchupProjection,
    candidates: Iterable[FormMatchupProjection],
    *,
    expected_future_turns: int,
    transformation_opportunity_cost: float,
) -> str | None:
    """Shared tactical choice for any source-legal replacement-form ability.

    Source adapters must supply only certified, legal form projections and
    source-correct Action/Bonus Action, resource, HP and Temporary HP valuations.
    This does NOT grant a Druid or shapechanger new legal form options.
    """
    return choose_profitable_change_shape(
        current,
        candidates,
        expected_future_turns=expected_future_turns,
        change_shape_action_cost=transformation_opportunity_cost,
    )
