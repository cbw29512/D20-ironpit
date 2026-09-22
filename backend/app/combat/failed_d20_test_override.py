from __future__ import annotations

import logging
from typing import Literal

from app.domain.models import CombatantState, DiceRoll, RollRevision

logger = logging.getLogger(__name__)
D20TestKind = Literal["attack", "saving_throw", "ability_check"]


def _selected_index(roll: DiceRoll) -> int:
    if not roll.rolls or roll.selected_roll is None:
        raise ValueError("Failed D20 override requires a concrete selected d20 roll.")
    if roll.mode.value == "advantage":
        return max(range(len(roll.rolls)), key=roll.rolls.__getitem__)
    if roll.mode.value == "disadvantage":
        return min(range(len(roll.rolls)), key=roll.rolls.__getitem__)
    return 0


def apply_failed_d20_test_override(
    state: CombatantState,
    roll: DiceRoll | None,
    *,
    failed: bool,
    test_kind: D20TestKind,
) -> tuple[DiceRoll | None, str | None, str | None]:
    """Replace one failed eligible D20 Test with the configured natural roll."""
    try:
        if not failed or roll is None:
            return roll, None, None

        for grant in state.template.progression_features.failed_d20_test_override_grants:
            if test_kind not in grant.test_kinds:
                continue
            resource = next((item for item in state.resources if item.id == grant.resource_id), None)
            if resource is None:
                raise ValueError(
                    f"Failed-D20 override {grant.source_id} references missing resource {grant.resource_id}."
                )
            if resource.current_uses <= 0:
                continue

            index = _selected_index(roll)
            replacement_rolls = list(roll.rolls)
            replacement_rolls[index] = grant.replacement_roll
            replacement_total = roll.total - (roll.selected_roll or 0) + grant.replacement_roll
            revision = RollRevision(
                source_effect_id=grant.source_id,
                kind="die_replacement",
                original_rolls=list(roll.rolls),
                replacement_rolls=replacement_rolls,
                original_modifier=roll.modifier,
                replacement_modifier=roll.modifier,
                original_selected=roll.selected_roll,
                replacement_selected=grant.replacement_roll,
                original_total=roll.total,
                replacement_total=replacement_total,
                accepted="replacement",
                replaced_die_index=index,
            )
            resource.current_uses -= 1
            revised = roll.model_copy(update={
                "rolls": replacement_rolls,
                "selected_roll": grant.replacement_roll,
                "total": replacement_total,
                "revisions": [*roll.revisions, revision],
            })
            return revised, grant.source_id, grant.source_name
        return roll, None, None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply D20 Test override for %s.", state.template.name)
        raise RuntimeError("Failed D20 Test override could not be resolved.") from exc


def source_name_for_roll(state: CombatantState, roll: DiceRoll | None) -> str | None:
    """Recover the player-facing source name from a recorded override revision."""
    try:
        if roll is None:
            return None
        source_ids = {item.source_effect_id for item in roll.revisions}
        for grant in reversed(state.template.progression_features.failed_d20_test_override_grants):
            if grant.source_id in source_ids:
                return grant.source_name
        return None
    except Exception as exc:
        logger.exception("Failed to recover D20 override source name for %s.", state.template.name)
        raise RuntimeError("D20 override source name could not be resolved.") from exc
