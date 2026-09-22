from __future__ import annotations

import logging

from app.combat.resources import resource_available, spend_resource
from app.domain.models import CombatantState, DiceRoll, RollRevision

logger = logging.getLogger(__name__)


def replace_failed_d20_with_natural_20(
    state: CombatantState,
    roll: DiceRoll,
    dc: int,
) -> tuple[DiceRoll, bool]:
    """Replace a failed D20 Test's selected d20 with 20 using a declared finite resource."""
    try:
        resource_id = state.template.progression_features.failed_d20_to_natural_20_resource_id
        if not resource_id or roll.total >= dc or not resource_available(state, resource_id):
            return roll, False
        selected = roll.selected_roll
        if selected is None:
            return roll, False
        replacement_rolls = list(roll.rolls)
        try:
            replaced_index = replacement_rolls.index(selected)
        except ValueError:
            raise ValueError("Selected d20 result is not present in the recorded roll set.")
        replacement_rolls[replaced_index] = 20
        replacement_total = roll.total + (20 - selected)
        revision = RollRevision(
            source_effect_id=resource_id,
            kind="selected_die_replacement",
            original_rolls=list(roll.rolls),
            replacement_rolls=replacement_rolls,
            original_modifier=roll.modifier,
            replacement_modifier=roll.modifier,
            original_selected=selected,
            replacement_selected=20,
            original_total=roll.total,
            replacement_total=replacement_total,
            accepted="replacement",
            replaced_die_index=replaced_index,
        )
        spend_resource(state, resource_id)
        return roll.model_copy(update={
            "rolls": replacement_rolls,
            "selected_roll": 20,
            "total": replacement_total,
            "notation": f"{roll.notation} [{resource_id}]",
            "revisions": [*roll.revisions, revision],
        }), True
    except Exception as exc:
        logger.exception("Failed D20 override failed for %s.", state.template.name)
        raise RuntimeError("Failed D20 override could not be resolved.") from exc
