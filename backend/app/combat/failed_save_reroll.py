from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.rolls import roll_d20
from app.domain.models import CombatantState, DiceRoll, RollMode, RollRevision

logger = logging.getLogger(__name__)


def _d20_count(mode: RollMode) -> int:
    return 1 if mode is RollMode.NORMAL else 2


def apply_failed_save_reroll(
    state: CombatantState,
    original: DiceRoll,
    dice: DiceProvider,
) -> tuple[DiceRoll, str | None, str | None]:
    """Spend the first eligible grant and reroll only the d20 portion of a failed save."""
    try:
        for grant in state.template.progression_features.failed_save_reroll_grants:
            resource = next((item for item in state.resources if item.id == grant.resource_id), None)
            if resource is None:
                raise ValueError(
                    f"Failed-save reroll {grant.source_id} references missing resource {grant.resource_id}."
                )
            if resource.current_uses < grant.resource_cost:
                continue

            d20_count = _d20_count(original.mode)
            retained_bonus_rolls = list(original.rolls[d20_count:])
            replacement_base = roll_d20(dice, original.modifier, original.mode)
            replacement_total = replacement_base.total + sum(retained_bonus_rolls)
            replacement_rolls = [*replacement_base.rolls, *retained_bonus_rolls]
            revision = RollRevision(
                source_effect_id=grant.source_id,
                kind="full_reroll",
                original_rolls=list(original.rolls),
                replacement_rolls=replacement_rolls,
                original_modifier=original.modifier,
                replacement_modifier=original.modifier,
                original_selected=original.selected_roll,
                replacement_selected=replacement_base.selected_roll,
                original_total=original.total,
                replacement_total=replacement_total,
                accepted="replacement",
            )
            resource.current_uses -= grant.resource_cost
            revised = original.model_copy(update={
                "notation": f"{original.notation} [{grant.source_name}]",
                "rolls": replacement_rolls,
                "selected_roll": replacement_base.selected_roll,
                "total": replacement_total,
                "revisions": [*original.revisions, revision],
            })
            return revised, grant.source_id, grant.source_name
        return original, None, None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply failed-save reroll for %s.", state.template.name)
        raise RuntimeError("Failed saving-throw reroll could not be resolved.") from exc
