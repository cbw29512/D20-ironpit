"""Universal movement-step entry triggers for source-declared passive abilities."""
from __future__ import annotations

import logging

from app.combat.damage import roll_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.on_hit_recurring_damage import apply_recurring_damage_effect
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_creature_space_entry(
    sequence: int, round_number: int, mover: EncounterCombatant,
    setup: EncounterSetup, dice, turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Apply each passive to each first entered occupied square per owner's turn."""
    try:
        if mover.state.position is None or not turn_key:
            raise ValueError("Creature-space entry requires a grid position and turn key.")
        actions = [
            action for action in mover.state.template.timed_self_buff_actions
            if action.activation_timing == "passive"
            and action.creature_space_entry_damage is not None
        ]
        if not actions:
            return [], sequence
        members = [*setup.heroes, *setup.monsters]
        affected = [member.state for member in members]
        events: list[BattleEvent] = []
        for target in members:
            if (target.combatant_id == mover.combatant_id
                or target.state.position != mover.state.position
                or target.state.is_dead or not target.state.is_alive):
                continue
            for action in actions:
                marker = f"creature-space:{action.id}:{target.combatant_id}"
                if mover.state.feature_last_turn_keys.get(marker) == turn_key:
                    continue
                mover.state.feature_last_turn_keys[marker] = turn_key
                spec = action.creature_space_entry_damage
                component = roll_damage_component(
                    dice, action.name, spec.dice_count, spec.dice_size,
                    0, spec.damage_type, False,
                )
                before = target.state.current_hp
                applied, components = apply_damage_defenses(target.state, [component])
                if applied:
                    apply_damage(
                        target.state, applied, damage_types={spec.damage_type},
                        dice=dice, affected_states=affected, setup=setup,
                        damage_components=components, source_id=mover.combatant_id,
                    )
                applied_burning = apply_recurring_damage_effect(
                    target.state, spec.recurring_damage,
                    source_id=mover.combatant_id,
                    source_effect_id=action.id, source_name=action.name,
                )
                events.append(BattleEvent(
                    sequence=sequence, round_number=round_number,
                    event_type="feature",
                    actor_id=mover.combatant_id, actor_name=mover.state.template.name,
                    target_id=target.combatant_id, target_name=target.state.template.name,
                    feature_id=action.name, hp_before=before,
                    hp_after=target.state.current_hp, is_dead=target.state.is_dead,
                    damage_components=components, animation=action.animation,
                    description=(
                        f"{action.name}: {mover.state.template.name} enters "
                        f"{target.state.template.name}'s space, dealing {applied} "
                        f"{spec.damage_type.value} damage"
                        + (" and igniting the target." if applied_burning else ".")
                    ),
                ))
                sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed creature-space entry effects for %s.", mover.combatant_id)
        raise
