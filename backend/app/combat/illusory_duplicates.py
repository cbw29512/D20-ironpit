from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.ability_score_reduction import effective_ability_modifier
from app.combat.effective_senses import effective_sense_range_ft
from app.combat.rolls import roll_d20
from app.combat.visibility_rules import can_see
from app.domain.models import CombatantState, DiceRoll, RollMode, TimedEffect

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IllusoryDuplicateInterception:
    effect: TimedEffect
    feature_id: str
    feature_name: str
    redirection_roll: DiceRoll
    target_ac: int


def intercept_attack(
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
    dice,
) -> IllusoryDuplicateInterception | None:
    """Redirect one attack to a live duplicate when its declarative rule succeeds."""
    try:
        if not can_see(attacker, defender, distance_ft):
            return None
        for effect in defender.timed_effects:
            if effect.illusory_duplicates_remaining <= 0 or effect.source_effect_id is None:
                continue
            actions = [
                action for action in defender.template.timed_self_buff_actions
                if action.id == effect.source_effect_id
                and action.illusory_duplicate_defense is not None
            ]
            if len(actions) != 1:
                raise ValueError("A live duplicate effect requires one declarative source action.")
            action = actions[0]
            rule = action.illusory_duplicate_defense
            if any(
                effective_sense_range_ft(attacker, sense_id) >= distance_ft
                for sense_id in rule.bypass_attacker_senses
            ):
                return None
            remaining = effect.illusory_duplicates_remaining
            if remaining >= len(rule.redirect_minimum_by_duplicates):
                raise ValueError("Duplicate count exceeds its source threshold table.")
            redirection = roll_d20(dice, 0, RollMode.NORMAL)
            if redirection.total < rule.redirect_minimum_by_duplicates[remaining]:
                return None
            return IllusoryDuplicateInterception(
                effect=effect,
                feature_id=action.id,
                feature_name=action.name,
                redirection_roll=redirection,
                target_ac=(
                    rule.armor_class_base
                    + effective_ability_modifier(defender, rule.armor_class_ability)
                ),
            )
        return None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Illusory duplicate interception failed for %s.", defender.template.name)
        raise RuntimeError("Illusory duplicate interception could not be resolved.") from exc


def consume_hit(defender: CombatantState, interception: IllusoryDuplicateInterception) -> int:
    """Destroy exactly one fight-local duplicate and end the group at zero."""
    effect = interception.effect
    if effect not in defender.timed_effects or effect.illusory_duplicates_remaining <= 0:
        raise ValueError("The intercepted duplicate is no longer active.")
    effect.illusory_duplicates_remaining -= 1
    if effect.illusory_duplicates_remaining == 0:
        from app.combat.timed_condition_lifecycle import remove_effect_group
        remove_effect_group(defender, effect)
    return effect.illusory_duplicates_remaining
