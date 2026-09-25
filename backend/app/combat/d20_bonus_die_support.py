from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.encounter_targeting import combatant_distance
from app.combat.pit_policy import is_backline
from app.domain.d20_bonus_dice import D20BonusDieAction
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def resource_for(member: EncounterCombatant, action: D20BonusDieAction):
    try:
        return next((item for item in member.state.resources if item.id == action.resource_id), None)
    except Exception as exc:
        logger.exception("D20 bonus-die resource lookup failed for %s.", member.combatant_id)
        raise RuntimeError("D20 bonus-die resource could not be resolved.") from exc


def target_allowed(
    source: EncounterCombatant,
    target: EncounterCombatant,
    action: D20BonusDieAction,
) -> bool:
    try:
        if target.state.is_dead or not target.state.is_alive:
            return False
        if action.target_mode == "self" and target.combatant_id != source.combatant_id:
            return False
        if action.target_mode == "other_ally" and (
            target.side != source.side or target.combatant_id == source.combatant_id
        ):
            return False
        if action.target_mode == "ally" and target.side != source.side:
            return False
        return combatant_distance(source, target) <= action.range_ft
    except Exception as exc:
        logger.exception(
            "Failed to validate d20 bonus-die target %s from %s.",
            target.combatant_id,
            source.combatant_id,
        )
        raise RuntimeError("D20 bonus-die target could not be validated.") from exc


def grant_conflicts(
    source: EncounterCombatant,
    target: EncounterCombatant,
    action: D20BonusDieAction,
    round_number: int,
) -> bool:
    try:
        return any(
            item.expires_round > round_number and (
                (item.source_id == source.combatant_id and item.source_effect_id == action.id)
                or (
                    action.exclusive_group is not None
                    and item.exclusive_group == action.exclusive_group
                )
            )
            for item in target.state.active_d20_bonus_dice
        )
    except Exception as exc:
        logger.exception("Failed to evaluate d20 bonus-die grant conflicts for %s.", target.combatant_id)
        raise RuntimeError("D20 bonus-die grant conflict could not be evaluated.") from exc


def choose_d20_bonus_die_action(
    source: EncounterCombatant,
    setup: EncounterSetup,
    round_number: int,
) -> tuple[D20BonusDieAction, EncounterCombatant] | None:
    """Choose one legal support grant without embedding source/class identity."""
    try:
        choices: list[tuple[D20BonusDieAction, EncounterCombatant]] = []
        allies = setup.heroes if source.side == "heroes" else setup.monsters
        for action in source.state.template.d20_bonus_die_actions:
            if not is_available(source.state, action.action_cost):
                continue
            resource = resource_for(source, action)
            if resource is None or resource.current_uses < action.resource_cost:
                continue
            for target in allies:
                if (
                    target_allowed(source, target, action)
                    and not grant_conflicts(source, target, action, round_number)
                ):
                    choices.append((action, target))
        if not choices:
            return None
        return min(
            choices,
            key=lambda choice: (
                -choice[0].priority,
                int(is_backline(choice[1])),
                -choice[1].state.template.weapon_attack.attack_bonus,
                choice[1].combatant_id,
            ),
        )
    except Exception as exc:
        logger.exception("Failed to choose d20 bonus-die support action for %s.", source.combatant_id)
        raise RuntimeError("D20 bonus-die support choice could not be resolved.") from exc
