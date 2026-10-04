from __future__ import annotations

import logging

from app.combat.condition_rules import can_see
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def eligible_area_spell_allies(
    caster: EncounterCombatant,
    setup: EncounterSetup,
    action: SpellSaveAction,
    slot_level: int,
) -> tuple[set[str], int]:
    """Return source-visible allies eligible for a declared area-spell protection grant."""
    try:
        grant = caster.state.template.progression_features.area_spell_ally_protection
        if grant is None or action.id not in grant.eligible_spell_ids:
            return set(), 0
        allies = setup.heroes if caster.side == "heroes" else setup.monsters
        eligible = {
            ally.combatant_id
            for ally in allies
            if ally.combatant_id != caster.combatant_id
            and ally.state.is_alive
            and not ally.state.is_dead
            and ally.state.current_hp > 0
            and (not grant.requires_source_sight or can_see(caster.state, ally.state, combatant_distance(caster, ally)))
        }
        limit = grant.base_protected_allies + grant.protected_allies_per_slot_level * slot_level
        return eligible, limit
    except Exception:
        logger.exception(
            "Failed to evaluate area-spell ally protection for %s using %s.",
            caster.combatant_id,
            action.id,
        )
        raise
