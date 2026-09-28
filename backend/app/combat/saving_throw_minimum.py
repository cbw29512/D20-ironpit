from __future__ import annotations

import logging

from app.domain.models import CombatantState, DiceRoll, RollRevision

logger = logging.getLogger(__name__)


def apply_saving_throw_minimum(
    state: CombatantState,
    ability: str,
    roll: DiceRoll,
) -> DiceRoll:
    """Apply the strongest declared minimum to an already-resolved saving throw."""
    try:
        rules = [
            rule for rule in state.template.progression_features.saving_throw_minimums
            if rule.ability == ability
        ]
        if not rules:
            return roll
        scores = state.template.ability_scores
        if scores is None:
            raise ValueError(
                f"{state.template.name} has a saving-throw minimum without certified ability scores."
            )
        floor = scores.score(ability)
        if roll.total >= floor:
            return roll
        rule = sorted(rules, key=lambda item: item.source_id)[0]
        revision = RollRevision(
            source_effect_id=rule.source_id,
            kind="total_replacement",
            original_rolls=list(roll.rolls),
            replacement_rolls=list(roll.rolls),
            original_modifier=roll.modifier,
            replacement_modifier=roll.modifier,
            original_selected=roll.selected_roll,
            replacement_selected=roll.selected_roll,
            original_total=roll.total,
            replacement_total=floor,
            accepted="replacement",
        )
        return roll.model_copy(update={
            "notation": f"{roll.notation} [{rule.source_id}]",
            "total": floor,
            "revisions": [*roll.revisions, revision],
        })
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to apply saving-throw minimum for %s (%s).",
            state.template.name,
            ability,
        )
        raise RuntimeError("Saving-throw minimum could not be applied.") from exc
