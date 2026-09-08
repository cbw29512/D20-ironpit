from __future__ import annotations

from app.combat.pit_policy import save_distance, target_order
from app.combat.saving_throws import legal_save_action, save_action_resource_available
from app.domain.encounters import EncounterCombatant, EncounterSetup


def choose_single_target_save(attacker: EncounterCombatant, setup: EncounterSetup):
    """Choose the first legal source-defined single-target save action."""
    for target in target_order(attacker, setup):
        for action in attacker.state.template.saving_throw_actions:
            if action.area is not None or not save_action_resource_available(attacker.state, action):
                continue
            distance = save_distance(attacker, target, action.range_ft)
            if legal_save_action(action, target, distance):
                return target, action, distance
    return None
