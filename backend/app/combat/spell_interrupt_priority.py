"""Universal initiative-ordered spell-interruption decision dispatch.

Input is a resolved encounter initiative order and source-declared actions.
No creature-name or spell-name dispatch; no new mutable combat state.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from app.combat.spell_interrupt_reactions import interrupt_legal, resolve_spell_interrupt
from app.domain.spell_interrupt_reactions import SpellInterruptReaction

logger = logging.getLogger(__name__)


def dispatch_spell_interrupts(
    sequence: int,
    round_number: int,
    caster,
    setup,
    initiative_order: Sequence[str],
    reactions_by_id: Mapping[str, Sequence[SpellInterruptReaction]],
    spell_name: str,
    spell_level: int,
    dice,
    *,
    is_spell_cast: bool,
):
    """Return (events, stopped, next_sequence) after one trigger window.

    Failed checks leave the original spell pending, so lower-initiative casters
    may legally respond. A successful interruption ends the decision scan.
    """
    try:
        members = {
            member.combatant_id: member
            for member in [*setup.heroes, *setup.monsters]
        }
        order = tuple(initiative_order)
        if (
            not order or len(order) != len(members)
            or len(set(order)) != len(order) or set(order) != set(members)
        ):
            raise ValueError("Reaction priority requires the complete resolved initiative order.")
        if not set(reactions_by_id).issubset(members):
            raise ValueError("Reaction source references a missing combatant.")
        if not isinstance(is_spell_cast, bool):
            raise ValueError("Spell-casting provenance must be explicitly typed.")
        if not is_spell_cast:
            return [], False, sequence

        events = []
        for combatant_id in order:
            interrupter = members[combatant_id]
            for action in reactions_by_id.get(combatant_id, ()):
                if not isinstance(action, SpellInterruptReaction):
                    raise ValueError("Spell interrupt must be a source-validated reaction.")
                if not interrupt_legal(
                    interrupter, caster, action, spell_level, is_spell_cast=True,
                ):
                    continue
                event, interrupted = resolve_spell_interrupt(
                    sequence, round_number, interrupter, caster, setup,
                    action, spell_name, spell_level, dice, is_spell_cast=True,
                )
                events.append(event)
                sequence += 1
                if interrupted:
                    return events, True, sequence
        return events, False, sequence
    except Exception:
        logger.exception(
            "Initiative-order casting interruption failed for %s.",
            caster.combatant_id,
        )
        raise
