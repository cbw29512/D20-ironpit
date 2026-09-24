from __future__ import annotations

import logging
from typing import Literal

from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DiceRoll, RollRevision

logger = logging.getLogger(__name__)
D20BonusKind = Literal["saving_throw", "ability_check"]


def apply_failed_d20_bonus_die(
    state: CombatantState,
    original: DiceRoll,
    dc: int,
    dice: DiceProvider,
    *,
    test_kind: D20BonusKind,
) -> tuple[DiceRoll, str | None, str | None]:
    """Spend the first eligible grant and add its die to a failed D20 Test."""
    try:
        if original.total >= dc:
            return original, None, None
        for grant in state.template.progression_features.failed_d20_bonus_die_grants:
            if test_kind not in grant.test_kinds:
                continue
            resource = next((item for item in state.resources if item.id == grant.resource_id), None)
            if resource is None:
                raise ValueError(
                    f"Failed-D20 bonus {grant.source_id} references missing resource {grant.resource_id}."
                )
            if resource.current_uses < grant.resource_cost:
                continue

            bonus = dice.roll(grant.dice_size)
            replacement_rolls = [*original.rolls, bonus]
            replacement_total = original.total + bonus
            revision = RollRevision(
                source_effect_id=grant.source_id,
                kind="additive_die",
                original_rolls=list(original.rolls),
                replacement_rolls=replacement_rolls,
                original_modifier=original.modifier,
                replacement_modifier=original.modifier,
                original_selected=original.selected_roll,
                replacement_selected=original.selected_roll,
                original_total=original.total,
                replacement_total=replacement_total,
                accepted="replacement",
            )
            resource.current_uses -= grant.resource_cost
            revised = original.model_copy(update={
                "notation": f"{original.notation} + 1d{grant.dice_size} [{grant.source_name}]",
                "rolls": replacement_rolls,
                "total": replacement_total,
                "revisions": [*original.revisions, revision],
            })
            return revised, grant.source_id, grant.source_name
        return original, None, None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply D20 bonus die for %s.", state.template.name)
        raise RuntimeError("Failed D20 Test bonus die could not be resolved.") from exc
