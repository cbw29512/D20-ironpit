from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.hit_point_loss import lose_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.ongoing_hp_loss import OngoingHpLossEffectDefinition, OngoingHpLossState
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def has_ongoing_hp_loss(state: CombatantState, effect_id: str) -> bool:
    try:
        return any(effect.effect_id == effect_id for effect in state.ongoing_hp_loss_effects)
    except Exception as exc:
        logger.exception("Failed ongoing HP-loss lookup for %s.", state.template.name)
        raise RuntimeError("Ongoing HP-loss state could not be inspected.") from exc


def apply_ongoing_hp_loss(
    state: CombatantState,
    source_id: str,
    source_effect_id: str,
    effect: OngoingHpLossEffectDefinition,
    round_number: int,
) -> str | None:
    try:
        if has_ongoing_hp_loss(state, effect.effect_id):
            return None
        state.ongoing_hp_loss_effects.append(OngoingHpLossState(
            effect_id=effect.effect_id,
            name=effect.name,
            source_id=source_id,
            source_effect_id=source_effect_id,
            applied_round=round_number,
            expires_round=round_number + effect.duration_rounds,
            timing=effect.timing,
            dice_count=effect.dice_count,
            dice_size=effect.dice_size,
            ends_on_spell_healing=effect.ends_on_spell_healing,
            removal_ability=effect.removal_ability,
            removal_skill=effect.removal_skill,
            removal_dc=effect.removal_dc,
            removal_range_ft=effect.removal_range_ft,
        ))
        return effect.effect_id
    except Exception as exc:
        logger.exception("Failed to apply ongoing HP loss %s.", effect.effect_id)
        raise RuntimeError("Ongoing HP-loss effect could not be applied.") from exc


def remove_on_spell_healing(state: CombatantState) -> list[str]:
    try:
        removed = [
            effect.effect_id
            for effect in state.ongoing_hp_loss_effects
            if effect.ends_on_spell_healing
        ]
        if removed:
            state.ongoing_hp_loss_effects = [
                effect for effect in state.ongoing_hp_loss_effects
                if not effect.ends_on_spell_healing
            ]
        return list(dict.fromkeys(removed))
    except Exception as exc:
        logger.exception("Failed spell-healing wound cleanup for %s.", state.template.name)
        raise RuntimeError("Spell-healing wound cleanup failed.") from exc


def resolve_start_turn_hp_loss(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    try:
        member.state.ongoing_hp_loss_effects = [
            effect for effect in member.state.ongoing_hp_loss_effects
            if round_number < effect.expires_round
        ]
        events: list[BattleEvent] = []
        affected = [item.state for item in [*setup.heroes, *setup.monsters]]
        for effect in list(member.state.ongoing_hp_loss_effects):
            if effect.timing != "target_turn_start" or member.state.is_dead:
                continue
            hp_before = member.state.current_hp
            rolled = [dice.roll(effect.dice_size) for _ in range(effect.dice_count)]
            lost = lose_hit_points(
                member.state, sum(rolled), affected_states=affected,
            )
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=member.combatant_id,
                actor_name=member.state.template.name,
                target_id=member.combatant_id,
                target_name=member.state.template.name,
                feature_id=effect.effect_id,
                hp_before=hp_before,
                hp_after=member.state.current_hp,
                is_dead=member.state.is_dead,
                animation="feature",
                description=(
                    f"{member.state.template.name} loses {lost} Hit Points from "
                    f"{effect.name} at the start of its turn (not damage)."
                ),
            ))
            sequence += 1
        return events, sequence
    except Exception as exc:
        logger.exception("Start-turn HP-loss resolution failed for %s.", member.combatant_id)
        raise RuntimeError("Start-turn HP loss could not be resolved.") from exc
