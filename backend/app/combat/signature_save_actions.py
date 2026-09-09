from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.area_saves import resolve_area_save_action
from app.combat.area_targeting import area_target_ids
from app.combat.saving_throws import save_action_resource_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_signature_area_save(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int, bool]:
    """Use a legal limited/resource-backed area action aggressively when available."""
    if not is_available(actor.state, "action"):
        return [], sequence, False
    for action in actor.state.template.saving_throw_actions:
        if action.area is None or action.resource_id is None:
            continue
        if not save_action_resource_available(actor.state, action):
            continue
        if not area_target_ids(actor, setup, action):
            continue
        events, sequence = resolve_area_save_action(sequence, round_number, actor, setup, action, dice)
        return events, sequence, True
    return [], sequence, False
