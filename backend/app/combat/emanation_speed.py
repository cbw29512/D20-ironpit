from __future__ import annotations

import logging

from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)


def _active_speed_emanations(setup: EncounterSetup):
    members = [*setup.heroes, *setup.monsters]
    for source in members:
        active_ids = {
            effect.source_effect_id
            for effect in source.state.timed_effects
            if effect.source_id == source.combatant_id and effect.source_effect_id
        }
        for action in source.state.template.timed_self_buff_actions:
            emanation = action.start_turn_emanation_damage
            if action.id in active_ids and emanation is not None and emanation.speed_multiplier < 1.0:
                yield source, action, emanation


def sync_emanation_speed(setup: EncounterSetup) -> None:
    """Keep live speed-halving auras aligned with who is currently inside them."""
    try:
        wanted: set[str] = set()
        for source, action, emanation in _active_speed_emanations(setup):
            enemies = setup.monsters if source.side == "heroes" else setup.heroes
            for target in enemies:
                if not target.state.is_alive or target.state.is_dead:
                    continue
                if combatant_distance(source, target) > emanation.radius_ft:
                    continue
                modifier_id = f"{source.combatant_id}:{action.id}:speed:{target.combatant_id}"
                wanted.add(modifier_id)
                if any(item.id == modifier_id for item in target.state.active_modifiers):
                    continue
                add_modifier(target.state, CombatModifier(
                    id=modifier_id,
                    source_id=source.combatant_id,
                    source_effect_id=action.id,
                    source_name=action.name,
                    source_is_magical=True,
                    kind=ModifierKind.SPEED_MULTIPLIER,
                    multiplier=emanation.speed_multiplier,
                    concentration_required=action.concentration,
                ))
        for member in [*setup.heroes, *setup.monsters]:
            member.state.active_modifiers = [
                item
                for item in member.state.active_modifiers
                if not (
                    item.kind is ModifierKind.SPEED_MULTIPLIER
                    and item.id.endswith(f":speed:{member.combatant_id}")
                    and item.id not in wanted
                    and ":speed:" in item.id
                )
            ]
    except Exception:
        logger.exception("Failed to sync emanation speed multipliers.")
        raise
