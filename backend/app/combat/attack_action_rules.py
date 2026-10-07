from __future__ import annotations

import logging

from app.domain.attack_action_definitions import AttackActionDefinition, all_action_slots
from app.domain.encounters import EncounterCombatant


logger = logging.getLogger(__name__)


def validate_attack_action_slots(attacker: EncounterCombatant) -> None:
    try:
        definition = attacker.state.template.attack_action
        if definition is None:
            raise ValueError("Combatant has no Multiattack action.")
        AttackActionDefinition.model_validate(definition.model_dump())
        profiles = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
        by_id = {attack.id: attack for attack in profiles}
        attacks = {
            attacker.state.template.weapon_attack.id,
            *(attack.id for attack in attacker.state.template.alternate_weapon_attacks),
        }
        saves = {action.id for action in attacker.state.template.saving_throw_actions}
        for slot in all_action_slots(definition):
            unknown = (set(slot.attack_ids) - attacks) | (set(slot.save_action_ids) - saves)
            if unknown:
                raise ValueError(f"Unknown Multiattack IDs in {definition.name}: {sorted(unknown)}")
        for variant in definition.variants:
            if variant.attack_kind and any(by_id[i].weapon.attack_kind != variant.attack_kind
                                           for slot in variant.slots for i in slot.attack_ids):
                raise ValueError("Multiattack variant contradicts its attack kind.")
    except Exception:
        logger.exception("Multiattack slot validation failed for %s.", attacker.combatant_id)
        raise
