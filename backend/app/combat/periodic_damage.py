from __future__ import annotations

import logging

from app.combat.damage import aggregate_damage_components, roll_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage
from app.domain.actions import ConditionTiming
from app.domain.models import BattleEvent, EncounterCombatant, TimedEffect

logger = logging.getLogger(__name__)


def periodic_damage_due(effect: TimedEffect, timing: ConditionTiming) -> bool:
    return effect.periodic_damage_timing == timing


def resolve_periodic_damage(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    effect: TimedEffect,
    dice,
) -> BattleEvent:
    """Apply one typed periodic-damage tick through the normal defense and HP pipelines."""
    try:
        damage_type = effect.periodic_damage_type
        if damage_type is None or effect.periodic_damage_dice_count < 1:
            raise ValueError("Periodic damage runtime state is incomplete.")
        hp_before = target.state.current_hp
        component = roll_damage_component(
            dice=dice,
            source=effect.source_effect_id or effect.effect_id,
            dice_count=effect.periodic_damage_dice_count,
            dice_size=effect.periodic_damage_dice_size,
            modifier=effect.periodic_damage_bonus,
            damage_type=damage_type,
            critical=False,
        )
        applied_total, components = apply_damage_defenses(target.state, [component])
        apply_damage(target.state, applied_total, damage_types={damage_type}, dice=dice)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=target.combatant_id,
            actor_name=target.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            damage_roll=aggregate_damage_components(components),
            damage_components=components,
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            feature_id=effect.source_effect_id or "periodic-damage",
            animation="damage",
            description=(
                f"{target.state.template.name} takes {applied_total} {damage_type.value} damage "
                f"from {effect.source_effect_id or effect.effect_id}."
            ),
        )
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Periodic damage failed for %s.", target.combatant_id)
        raise RuntimeError("Periodic damage could not be resolved.") from exc
