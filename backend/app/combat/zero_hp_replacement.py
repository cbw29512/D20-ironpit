from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import CombatantState
from app.domain.zero_hp_replacement import (
    ZeroHpReplacementEffectDefinition,
    ZeroHpReplacementState,
)

logger = logging.getLogger(__name__)


def apply_zero_hp_replacement_effect(
    target: CombatantState,
    source_id: str,
    source_effect_id: str,
    effect: ZeroHpReplacementEffectDefinition,
) -> str:
    """Apply a source-owned debuff that replaces a later zero-HP outcome."""
    try:
        target.zero_hp_replacement = ZeroHpReplacementState(
            effect_id=effect.effect_id,
            source_id=source_id,
            source_effect_id=source_effect_id,
            replacement_mode=effect.replacement_mode,
            control_mode=effect.control_mode,
            replacement_hp=effect.replacement_hp,
        )
        if effect.effect_id not in target.active_effect_ids:
            target.active_effect_ids.append(effect.effect_id)
        return effect.effect_id
    except Exception as exc:
        logger.exception("Failed to apply zero-HP replacement effect %s.", effect.effect_id)
        raise RuntimeError("Zero-HP replacement effect could not be applied.") from exc


def activate_zero_hp_replacement(state: CombatantState) -> bool:
    """Replace the ordinary zero-HP transition while deferring template/control settlement."""
    try:
        rule = state.zero_hp_replacement
        if rule is None or rule.triggered:
            return False
        rule.triggered = True
        state.current_hp = rule.replacement_hp
        state.is_alive = True
        state.is_dead = False
        state.is_unconscious = False
        state.is_stable = False
        state.death_save_successes = 0
        state.death_save_failures = 0
        return True
    except Exception as exc:
        logger.exception("Failed to activate zero-HP replacement for %s.", state.template.name)
        raise RuntimeError("Zero-HP replacement could not be activated.") from exc


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def settle_zero_hp_replacement(target: EncounterCombatant, setup: EncounterSetup) -> bool:
    """Swap a triggered combatant to the source template and source-controlled encounter side."""
    try:
        rule = target.state.zero_hp_replacement
        if rule is None or not rule.triggered:
            return False
        source = next((member for member in _members(setup) if member.combatant_id == rule.source_id), None)
        if source is None:
            raise ValueError(f"Replacement source {rule.source_id!r} is not present in the encounter.")
        if rule.replacement_mode != "source-template" or rule.control_mode != "source-side":
            raise ValueError("Unsupported zero-HP replacement mode.")

        previous = target.state
        replacement = build_combatant_state(source.state.template)
        replacement.current_hp = min(rule.replacement_hp, replacement.template.max_hp)
        replacement.position = previous.position
        replacement.initiative_roll = previous.initiative_roll
        replacement.initiative_total = previous.initiative_total
        replacement.turn_serial = previous.turn_serial
        target.state = replacement

        if target.side != source.side:
            old_group = setup.heroes if target.side == "heroes" else setup.monsters
            new_group = setup.heroes if source.side == "heroes" else setup.monsters
            old_group[:] = [member for member in old_group if member.combatant_id != target.combatant_id]
            if all(member.combatant_id != target.combatant_id for member in new_group):
                new_group.append(target)
            target.side = source.side
        return True
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to settle zero-HP replacement for %s.", target.combatant_id)
        raise RuntimeError("Zero-HP replacement settlement failed.") from exc


__all__ = [
    "activate_zero_hp_replacement",
    "apply_zero_hp_replacement_effect",
    "settle_zero_hp_replacement",
]
