from __future__ import annotations

import logging

from app.combat.friendly_recovery_auras import (
    aura_is_active,
    encounter_members,
    heal_recovery_aura_target,
    target_in_aura,
)
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def resolve_source_turn_recovery_heals(
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> int:
    """Apply printed start-of-source-turn aura healing while the aura persists."""
    try:
        healed = 0
        for action in source.state.template.timed_self_buff_actions:
            aura = action.friendly_recovery_aura
            if aura is None or not aura.heal_on_source_turn_start:
                continue
            if not aura_is_active(source, action.id):
                continue
            healed += heal_recovery_aura_target(source, action, setup, dice)
        return healed
    except Exception:
        logger.exception("Failed source-turn recovery heal for %s.", source.combatant_id)
        raise


def resolve_zero_hp_ally_recovery(
    member: EncounterCombatant,
    setup: EncounterSetup,
) -> int:
    """Regain printed HP when an ally at 0 HP starts its turn inside the aura."""
    try:
        if member.state.current_hp != 0 or member.state.is_dead:
            return 0
        for source in encounter_members(setup):
            if source.combatant_id == member.combatant_id or source.side != member.side:
                continue
            for action in source.state.template.timed_self_buff_actions:
                aura = action.friendly_recovery_aura
                if aura is None or aura.zero_hp_ally_start_heal <= 0:
                    continue
                if not aura_is_active(source, action.id):
                    continue
                if not target_in_aura(source, member, aura.radius_ft):
                    continue
                return restore_hit_points(member.state, aura.zero_hp_ally_start_heal)
        return 0
    except Exception:
        logger.exception("Failed 0-HP ally recovery for %s.", member.combatant_id)
        raise
