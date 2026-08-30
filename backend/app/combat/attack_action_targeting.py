from __future__ import annotations

import logging

from app.combat.attack_legality import attack_allowed_against
from app.combat.encounter_targeting import combatant_distance, living_opponents, select_nearest_target
from app.domain.actions import AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def _slot_statically_allows(attacker: EncounterCombatant, target: EncounterCombatant, slot: AttackActionSlot) -> bool:
    attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
    if any(
        attack.id in slot.attack_ids
        and attack_allowed_against(attack, attacker.combatant_id, target.state)
        for attack in attacks
    ):
        return True
    allowed_saves = set(slot.save_action_ids)
    return any(
        action.id in allowed_saves
        and (action.target_max_size is None or size_at_most(target.state.template.size, action.target_max_size))
        for action in attacker.state.template.saving_throw_actions
    )


def select_slot_target(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    slot: AttackActionSlot,
) -> EncounterCombatant | None:
    """Choose the preferred target if this Multiattack slot can affect it, otherwise retarget legally."""
    try:
        preferred = select_nearest_target(attacker, setup)
        opponents = sorted(living_opponents(attacker, setup), key=lambda target: combatant_distance(attacker, target))
        candidates = ([preferred] if preferred is not None else []) + [target for target in opponents if target is not preferred]
        return next((target for target in candidates if _slot_statically_allows(attacker, target, slot)), None)
    except Exception as exc:
        logger.exception("Multiattack slot target selection failed for %s.", attacker.combatant_id)
        raise RuntimeError("Multiattack slot target could not be selected.") from exc
