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
    source_id: str | None = None,
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
        resource = None
        if defense.resource_id is not None:
            # Innate spell: source card supplies its daily-use pool.
            resource = next((item for item in state.resources
                             if item.id == defense.resource_id), None)
            if resource is None or resource.current_uses < 1:
                return False
        elif defense.minimum_slot_level is not None:
            # Prepared spell: consume the lowest legal available spell slot.
            slots = sorted(
                (int(item.id.removeprefix("spell-slot-")), item)
                for item in state.resources
                if item.id.startswith("spell-slot-")
                and item.id.removeprefix("spell-slot-").isdecimal()
                and int(item.id.removeprefix("spell-slot-")) >= defense.minimum_slot_level
                and item.current_uses > 0
            )
            if not slots:
                return False
            resource = slots[0][1]
        # At-will innate spells spend the Reaction but no finite resource.
        spend(state, "reaction")
        if resource is not None:
            resource.current_uses -= 1
        add_modifier(state, CombatModifier(
            id=f"{source_id or state.template.id}:{defense.id}:reaction",
            source_id=source_id or state.template.id, source_effect_id=defense.id,
            source_name=defense.name, source_is_magical=True,
            kind=ModifierKind.ARMOR_CLASS, flat_bonus=defense.ac_bonus,
            expires_at_start_of_source_turn=True,
        ))
        return True
    except Exception:
        logger.exception("Failed reaction defense for %s", state.template.name)
        raise


def reaction_defense_blocks_auto_hit(
    state: CombatantState, spell_id: str, *, source_id: str | None = None,
) -> bool:
    try:
        defense = state.template.reaction_defense_spell
        if defense is None or spell_id not in defense.blocked_auto_hit_spell_ids:
            return False
        if active_reaction_defense(state):
            return True
        return trigger_reaction_defense(
            state, incoming_auto_hit_id=spell_id, source_id=source_id,
        )
    except Exception:
        logger.exception("Failed to inspect auto-hit immunity for %s", state.template.name)
        raise
