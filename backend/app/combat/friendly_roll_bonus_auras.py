"""Dynamically project source-owned friendly bonus dice through the universal modifier stack."""
from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
PREFIX = "friendly-roll-bonus-aura:"


def sync_friendly_roll_bonus_auras(setup: EncounterSetup) -> None:
    """Recompute eligible recipients without mutating source templates."""
    try:
        for member in [*setup.heroes, *setup.monsters]:
            member.state.active_modifiers = [
                modifier for modifier in member.state.active_modifiers
                if not modifier.id.startswith(PREFIX)
            ]
        for side in (setup.heroes, setup.monsters):
            for source in side:
                state = source.state
                if state.is_dead or not state.is_alive or state.current_hp <= 0:
                    continue
                for action in state.template.timed_self_buff_actions:
                    aura = action.friendly_roll_bonus_aura
                    if aura is None:
                        continue
                    if not any(effect.source_id == source.combatant_id and
                               effect.source_effect_id == action.id for effect in state.timed_effects):
                        continue
                    for target in side:
                        if target.state.is_dead or not target.state.is_alive:
                            continue
                        if source.combatant_id == target.combatant_id and not aura.includes_source:
                            continue
                        if combatant_distance(source, target) > aura.radius_ft:
                            continue
                        if aura.requires_hearing and has_condition(target.state, "deafened"):
                            continue
                        for kind, count, size in (
                            (ModifierKind.ATTACK_ROLL_BONUS_DIE, aura.attack_dice_count, aura.attack_dice_size),
                            (ModifierKind.SAVING_THROW_BONUS_DIE, aura.save_dice_count, aura.save_dice_size),
                        ):
                            if not count:
                                continue
                            add_modifier(target.state, CombatModifier(
                                id=f"{PREFIX}{source.combatant_id}:{action.id}:{target.combatant_id}:{kind.value}",
                                source_id=source.combatant_id,
                                source_effect_id=action.id,
                                source_name=action.name,
                                kind=kind,
                                dice_count=count,
                                dice_size=size,
                            ))
    except Exception:
        logger.exception("Failed to synchronize friendly roll-bonus auras.")
        raise
