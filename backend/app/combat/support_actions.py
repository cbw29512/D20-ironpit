from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.dice import DiceProvider
from app.combat.modifier_stack import add_modifier
from app.combat.resources import resource_available, spend_resource
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.support_actions import CombatSupportAction

logger = logging.getLogger(__name__)


def choose_support_action(
    source: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[CombatSupportAction, EncounterCombatant] | None:
    """Choose a legal support action without inventing ally-priority heuristics."""
    try:
        for action in source.state.template.support_actions:
            if not is_available(source.state, action.action_cost):
                continue
            if not resource_available(source.state, action.resource_id, action.resource_cost):
                continue
            return action, source
        return None
    except Exception as exc:
        logger.exception("Failed support-action choice for %s.", source.combatant_id)
        raise RuntimeError("Support-action choice failed.") from exc


def resolve_support_action(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    target: EncounterCombatant,
    action: CombatSupportAction,
    dice: DiceProvider,
) -> BattleEvent:
    try:
        if not is_available(source.state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
        if not resource_available(source.state, action.resource_id, action.resource_cost):
            raise ValueError(f"{action.name} lacks its required resource.")

        rolls = [
            dice.roll(action.temporary_hp_dice_size)
            for _ in range(action.temporary_hp_dice_count)
        ]
        amount = max(0, sum(rolls) + action.temporary_hp_bonus)
        before = target.state.temporary_hp
        after = grant_temporary_hit_points(target.state, amount)

        if action.attack_roll_advantage_until_source_turn_start:
            add_modifier(target.state, CombatModifier(
                id=f"{source.combatant_id}:{action.id}:{target.combatant_id}:attack-advantage",
                source_id=source.combatant_id,
                source_effect_id=action.id,
                kind=ModifierKind.ATTACK_ROLL_ADVANTAGE,
                target_id=target.combatant_id,
                expires_at_start_of_source_turn=True,
            ))

        spend(source.state, action.action_cost)
        remaining = spend_resource(source.state, action.resource_id, action.resource_cost)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=source.combatant_id,
            actor_name=source.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            temporary_hp_before=before,
            temporary_hp_after=after,
            feature_id=action.id,
            resource_remaining=remaining,
            animation=action.animation,
            description=(
                f"{source.state.template.name} uses {action.name}; "
                f"{target.state.template.name} has {after} Temporary HP and "
                "Advantage on attack rolls until the source's next turn."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Support-action resolution failed for %s.", source.combatant_id)
        raise RuntimeError("Support-action resolution failed.") from exc
