from __future__ import annotations

import logging

from app.domain.models import CombatantState, DiceRoll, RollRevision
from app.domain.progression import D20TestKind

logger = logging.getLogger(__name__)


def _resource(state: CombatantState, resource_id: str):
    return next((item for item in state.resources if item.id == resource_id), None)


def apply_failed_d20_replacement(
    state: CombatantState,
    roll: DiceRoll,
    *,
    failed: bool,
    test_kind: D20TestKind,
) -> tuple[DiceRoll, str | None, str | None]:
    """Replace the selected d20 after a failed test using declarative source data."""
    try:
        if not failed:
            return roll, None, None
        rules = sorted(
            (
                rule
                for rule in state.template.progression_features.failed_d20_test_replacements
                if test_kind in rule.test_kinds
            ),
            key=lambda rule: rule.source_id,
        )
        for rule in rules:
            resource = _resource(state, rule.resource_id)
            if resource is None:
                raise ValueError(
                    f"{rule.source_name} references missing resource {rule.resource_id}."
                )
            if resource.current_uses <= 0:
                continue
            if roll.selected_roll is None:
                raise ValueError(f"{rule.source_name} requires a selected d20 roll.")

            d20_count = 1 if roll.mode.value == "normal" else 2
            candidate_rolls = list(roll.rolls)
            selected_index = next(
                (
                    index
                    for index, value in enumerate(candidate_rolls[:d20_count])
                    if value == roll.selected_roll
                ),
                None,
            )
            if selected_index is None:
                raise ValueError(
                    f"{rule.source_name} could not locate the selected d20 in roll evidence."
                )
            replacement_rolls = list(candidate_rolls)
            replacement_rolls[selected_index] = rule.replacement_roll
            replacement_total = roll.total - roll.selected_roll + rule.replacement_roll
            revision = RollRevision(
                source_effect_id=rule.source_id,
                kind="die_replacement",
                original_rolls=candidate_rolls,
                replacement_rolls=replacement_rolls,
                original_modifier=roll.modifier,
                replacement_modifier=roll.modifier,
                original_selected=roll.selected_roll,
                replacement_selected=rule.replacement_roll,
                original_total=roll.total,
                replacement_total=replacement_total,
                accepted="replacement",
                replaced_die_index=selected_index,
            )
            resource.current_uses -= 1
            return roll.model_copy(update={
                "notation": f"{roll.notation} [{rule.source_name}]",
                "rolls": replacement_rolls,
                "selected_roll": rule.replacement_roll,
                "total": replacement_total,
                "revisions": [*roll.revisions, revision],
            }), rule.source_id, rule.source_name
        return roll, None, None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed D20 Test replacement failed for %s.", state.template.name)
        raise RuntimeError("Failed D20 Test replacement could not be resolved.") from exc
