from __future__ import annotations

import logging

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



def apply_skill_check_d20_minimum(
    state: CombatantState,
    skill_id: str,
    roll: DiceRoll,
) -> DiceRoll:
    """Apply the strongest declared d20 floor for a proficient skill check."""
    try:
        rules = [
            rule for rule in state.template.progression_features.skill_check_d20_minimums
            if skill_id in rule.skill_ids
        ]
        if not rules:
            return roll
        if roll.selected_roll is None:
            raise ValueError("Skill-check d20 minimum requires a selected d20 roll.")
        rule = sorted(rules, key=lambda item: (-item.minimum_roll, item.source_id))[0]
        if roll.selected_roll >= rule.minimum_roll:
            return roll
        replacement_rolls = [max(value, rule.minimum_roll) for value in roll.rolls]
        replacement_selected = rule.minimum_roll
        replacement_total = replacement_selected + roll.modifier
        revision = RollRevision(
            source_effect_id=rule.source_id,
            kind="die_replacement",
            original_rolls=list(roll.rolls),
            replacement_rolls=replacement_rolls,
            original_modifier=roll.modifier,
            replacement_modifier=roll.modifier,
            original_selected=roll.selected_roll,
            replacement_selected=replacement_selected,
            original_total=roll.total,
            replacement_total=replacement_total,
            accepted="replacement",
        )
        return roll.model_copy(update={
            "rolls": replacement_rolls,
            "selected_roll": replacement_selected,
            "total": replacement_total,
            "notation": f"{roll.notation} [{rule.source_id}]",
            "revisions": [*roll.revisions, revision],
        })
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed to apply skill-check d20 minimum for %s (%s).",
            state.template.name,
            skill_id,
        )
        raise RuntimeError("Skill-check d20 minimum could not be applied.") from exc
