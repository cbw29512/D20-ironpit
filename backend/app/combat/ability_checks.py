from __future__ import annotations

import logging

from app.combat.d20_bonus_dice import (
    apply_d20_bonus_die_if_useful,
    apply_resource_backed_d20_bonus_if_useful,
)
from app.combat.dice import DiceProvider
from app.combat.failed_d20_test_override import apply_failed_d20_test_override
from app.domain.character_builds import AbilityName
from app.domain.models import CombatantState, DiceRoll, RollRevision

logger = logging.getLogger(__name__)


def apply_ability_check_minimum(
    state: CombatantState,
    ability: AbilityName,
    roll: DiceRoll,
) -> DiceRoll:
    """Apply the strongest declared minimum to an already-resolved ability check."""
    try:
        rules = [
            rule for rule in state.template.progression_features.ability_check_minimums
            if rule.ability == ability
        ]
        if not rules:
            return roll
        scores = state.template.ability_scores
        if scores is None:
            raise ValueError(
                f"{state.template.name} has an ability-check minimum without certified ability scores."
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
            "Failed to apply ability-check minimum for %s (%s).",
            state.template.name,
            ability,
        )
        raise RuntimeError("Ability-check minimum could not be applied.") from exc


def resolve_ability_check_outcome(
    state: CombatantState,
    ability: AbilityName,
    roll: DiceRoll,
    dc: int,
    *,
    dice: DiceProvider | None = None,
    round_number: int | None = None,
) -> tuple[DiceRoll, bool]:
    """Apply universal post-roll ability-check revisions, then test against the DC."""
    try:
        revised = apply_ability_check_minimum(state, ability, roll)
        if state.active_d20_bonus_dice:
            if dice is None or round_number is None:
                raise ValueError("Active d20 bonus die requires ability-check dice and round context.")
            revised, _ = apply_d20_bonus_die_if_useful(
                state, "ability_check", revised, dc, dice, round_number,
            )
        if state.template.progression_features.resource_backed_d20_bonus_dice:
            if dice is None:
                raise ValueError("Resource-backed ability-check bonus die requires dice context.")
            revised, _ = apply_resource_backed_d20_bonus_if_useful(
                state, "ability_check", revised, dc, dice,
            )
        revised, _, _ = apply_failed_d20_test_override(
            state, revised, failed=revised.total < dc, test_kind="ability_check",
        )
        if revised is None:
            raise ValueError("Ability-check override unexpectedly removed the d20 roll.")
        return revised, revised.total >= dc
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to resolve ability-check outcome for %s (%s).",
            state.template.name,
            ability,
        )
        raise RuntimeError("Ability-check outcome could not be resolved.") from exc
