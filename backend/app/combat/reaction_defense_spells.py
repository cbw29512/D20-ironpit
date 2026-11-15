"""Universal reaction defense activation via slots, action economy, AC modifiers."""
from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.modifier_stack import add_modifier, effective_armor_class
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def active_reaction_defense(state: CombatantState) -> bool:
    try:
        defense = state.template.reaction_defense_spell
        return bool(defense and any(
            modifier.kind is ModifierKind.ARMOR_CLASS
            and modifier.source_effect_id == defense.id
            and modifier.source_id == state.template.id
            for modifier in state.active_modifiers
        ))
    except Exception:
        logger.exception("Cannot inspect reaction defense for %s", state.template.name)
        raise


def trigger_reaction_defense(
    state: CombatantState, *,
    incoming_attack_total: int | None = None,
    natural_roll: int | None = None,
    incoming_auto_hit_id: str | None = None,
) -> bool:
    """Cast when the reaction changes an attack result or blocks an auto-hit."""
    try:
        defense = state.template.reaction_defense_spell
        if defense is None or active_reaction_defense(state):
            return False
        if not is_available(state, "reaction"):
            return False
        if incoming_auto_hit_id is not None:
            if incoming_auto_hit_id not in defense.blocked_auto_hit_spell_ids:
                return False
        else:
            if incoming_attack_total is None or natural_roll in {1, 20}:
                return False
            ac = effective_armor_class(state)
            if not ac <= incoming_attack_total < ac + defense.ac_bonus:
                return False
        slots = sorted(
            (int(resource.id.removeprefix("spell-slot-")), resource)
            for resource in state.resources
            if resource.id.startswith("spell-slot-")
            and resource.id.removeprefix("spell-slot-").isdecimal()
            and int(resource.id.removeprefix("spell-slot-")) >= defense.minimum_slot_level
            and resource.current_uses > 0
        )
        if not slots:
            return False
        _, slot = slots[0]
        # Check all eligibility before changing fight state.
        spend(state, "reaction")
        slot.current_uses -= 1
        add_modifier(state, CombatModifier(
            id=f"{state.template.id}:{defense.id}:reaction",
            source_id=state.template.id, source_effect_id=defense.id,
            source_name=defense.name, source_is_magical=True,
            kind=ModifierKind.ARMOR_CLASS, flat_bonus=defense.ac_bonus,
            expires_at_start_of_source_turn=True,
        ))
        return True
    except Exception:
        logger.exception("Failed reaction defense for %s", state.template.name)
        raise


def reaction_defense_blocks_auto_hit(state: CombatantState, spell_id: str) -> bool:
    try:
        defense = state.template.reaction_defense_spell
        if defense is None or spell_id not in defense.blocked_auto_hit_spell_ids:
            return False
        if active_reaction_defense(state):
            return True
        return trigger_reaction_defense(state, incoming_auto_hit_id=spell_id)
    except Exception:
        logger.exception("Failed to inspect auto-hit immunity for %s", state.template.name)
        raise
