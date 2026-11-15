"""2014 creature-targeted Dispel Magic: one cast, all tracked spell effects.

The shared resolver consumes the action/slot; this helper resolves each spell
on ONE target. Every effect has its own higher-level check and source cleanup.
"""
from __future__ import annotations

import logging

from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
from app.combat.effect_removal_targets import TrackedSpellEffect, removal_targets
from app.combat.modifier_stack import remove_source_modifiers
from app.combat.rolls import roll_d20
from app.domain.events import AuditPhase, AuditStep, EventAudit

logger = logging.getLogger(__name__)


def resolve_target_spell_effects(remover, setup, action, target, dice, round_number):
    """Return (removed spell IDs, first check, first DC, audit, description)."""
    try:
        candidates = [
            item for item in removal_targets(remover, setup, action)
            if isinstance(item, TrackedSpellEffect)
            and item.target.combatant_id == target.combatant_id
        ]
        if not candidates:
            raise ValueError("No tracked spell effects remain on the selected target.")
        # Preflight the entire cast before the caller spends any resources.
        higher = any(item.spell_level > action.auto_remove_max_level for item in candidates)
        if higher and (dice is None or remover.state.template.ability_scores is None):
            raise ValueError("Higher-level Dispel Magic checks require dice and casting ability scores.")
        return candidates
    except Exception:
        logger.exception("Failed Dispel Magic target-effect preflight")
        raise


def apply_target_spell_effects(remover, setup, action, target, candidates, dice, round_number):
    """Resolve independent checks; never infer an effect from a creature name."""
    try:
        removed = []
        audits = []
        summaries = []
        first_check = None
        first_dc = None
        for item in candidates:
            check, dc, succeeded = None, None, True
            if item.spell_level > action.auto_remove_max_level:
                dc = 10 + item.spell_level
                check = roll_d20(
                    dice,
                    remover.state.template.ability_scores.modifier(action.casting_ability),
                    ability_check_roll_mode(remover.state, ability=action.casting_ability),
                )
                check, succeeded = resolve_ability_check_outcome(
                    remover.state, action.casting_ability, check, dc,
                    dice=dice, round_number=round_number,
                    encounter_roller=remover, setup=setup,
                )
                if first_check is None:
                    first_check, first_dc = check, dc
                audits.append(AuditStep(
                    phase=AuditPhase.HIT_OR_SAVE_CHECK, kind="check",
                    label=(f"{item.effect_id} level {item.spell_level}: "
                           f"Dispel Magic check {check.total} vs DC {dc}; "
                           f"{'success' if succeeded else 'failure'}"),
                ))
            else:
                audits.append(AuditStep(
                    phase=AuditPhase.HIT_OR_SAVE_CHECK, kind="rule",
                    label=f"{item.effect_id} level {item.spell_level}: automatic dispel",
                ))
            if succeeded:
                remove_source_modifiers(
                    [target.state], item.source.combatant_id, item.effect_id,
                )
                # Only the targeted creature loses this spell's instance.
                # Other creatures affected by the same concentration remain.
                target.state.active_buff_effect_ids = [
                    name for name in target.state.active_buff_effect_ids
                    if name != item.effect_id
                ]
                removed.append(item.effect_id)
            summaries.append(f"{item.effect_id}: {'ended' if succeeded else 'resisted'}")
        return removed, first_check, first_dc, EventAudit(steps=audits), "; ".join(summaries)
    except Exception:
        logger.exception("Failed to resolve multiple tracked spell effects")
        raise
