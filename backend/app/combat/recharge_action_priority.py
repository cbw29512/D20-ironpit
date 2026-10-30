from __future__ import annotations

import logging

from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.pit_policy import choose_attack, save_distance, target_order
from app.combat.resources import action_resource_available
from app.combat.saving_throws import legal_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _recharge_resource_ids(actor: EncounterCombatant) -> set[str]:
    try:
        return {rule.resource_id for rule in actor.state.template.recharge_rules}
    except Exception:
        logger.exception("Failed to collect Recharge resources for %s.", actor.combatant_id)
        raise


def choose_priority_recharge_action(
    actor: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[str, object] | None:
    try:
        recharge_ids = _recharge_resource_ids(actor)
        if not recharge_ids:
            return None

        legal: list[tuple[str, object]] = []
        for action in actor.state.template.saving_throw_actions:
            if (
                action.action_cost != "action"
                or action.resource_id not in recharge_ids
                or not action_resource_available(actor.state, action)
            ):
                continue
            if action.area is not None:
                placements = legal_area_save_placements(actor, setup, action)
                if placements:
                    legal.append(("area-save", (action, placements[0])))
                continue
            for target in target_order(actor, setup):
                distance = save_distance(actor, target, action.range_ft)
                if legal_save_action(
                    action, target, distance,
                    source_id=actor.combatant_id, actor=actor,
                ):
                    legal.append(("save-action", (target, action, distance)))
                    break

        attacks = [
            attack for attack in [
                actor.state.template.weapon_attack,
                *actor.state.template.alternate_weapon_attacks,
            ]
            if attack is not None and attack.resource_id in recharge_ids
        ]
        if attacks:
            choice = choose_attack(actor, setup, [attack.id for attack in attacks])
            if choice is not None:
                legal.append(("standard-attack", choice))

        if len(legal) > 1:
            raise ValueError(
                "Multiple legal Recharge Action families require explicit source-priority policy."
            )
        return legal[0] if legal else None
    except Exception:
        logger.exception("Failed Recharge Action priority for %s.", actor.combatant_id)
        raise
