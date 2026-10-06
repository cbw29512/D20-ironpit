from __future__ import annotations

import logging

from app.domain.encounters import EncounterCombatant


logger = logging.getLogger(__name__)


def validate_attack_action_slots(attacker: EncounterCombatant) -> None:
    try:
        definition = attacker.state.template.attack_action
        if definition is None:
            raise ValueError("Combatant has no Multiattack action.")
        attacks = {
            attacker.state.template.weapon_attack.id,
            *(attack.id for attack in attacker.state.template.alternate_weapon_attacks),
        }
        saves = {action.id for action in attacker.state.template.saving_throw_actions}
        for slot in definition.slots:
            unknown = (set(slot.attack_ids) - attacks) | (set(slot.save_action_ids) - saves)
            if unknown:
                raise ValueError(f"Unknown Multiattack IDs in {definition.name}: {sorted(unknown)}")
    except Exception:
        logger.exception("Multiattack slot validation failed for %s.", attacker.combatant_id)
        raise
