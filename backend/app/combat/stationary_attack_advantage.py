from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.modifier_stack import (
    add_modifier,
    effective_speed,
    next_attack_against_advantage_sources,
)
from app.combat.pit_policy import choose_standard_attack
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)

STATIONARY_ATTACK_ADVANTAGE_EFFECT_ID = "stationary-attack-advantage"


def use_stationary_attack_advantage(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    *,
    feature_id: str,
) -> BattleEvent | None:
    """Trade a Bonus Action and all movement for Advantage on the next legal attack."""
    try:
        features = attacker.state.template.progression_features
        if not features.stationary_bonus_action_next_attack_advantage:
            return None
        if not is_available(attacker.state, "bonus_action"):
            return None
        speed = effective_speed(attacker.state)
        if attacker.state.movement_remaining_ft != speed:
            return None

        choice = choose_standard_attack(attacker, setup)
        if choice is None:
            return None
        target, _attack, _distance = choice
        if next_attack_against_advantage_sources(attacker.state, target.combatant_id):
            return None

        spend(attacker.state, "bonus_action")
        attacker.state.movement_remaining_ft = 0
        add_modifier(attacker.state, CombatModifier(
            id=f"{attacker.combatant_id}:{STATIONARY_ATTACK_ADVANTAGE_EFFECT_ID}:{target.combatant_id}",
            source_id=attacker.combatant_id,
            source_effect_id=feature_id,
            kind=ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE,
            target_id=target.combatant_id,
            expires_source_turn_end_round=round_number,
        ))
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=attacker.combatant_id,
            actor_name=attacker.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            feature_id=feature_id,
            animation="focus",
            description=(
                f"{attacker.state.template.name} gives up movement to focus on "
                f"{target.state.template.name}."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Stationary attack advantage failed for %s.", attacker.combatant_id)
        raise RuntimeError("Stationary attack advantage could not be resolved.") from exc
