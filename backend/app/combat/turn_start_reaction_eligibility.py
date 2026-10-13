from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.condition_rules import can_see
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant


def eligible_turn_start_reaction(
    source: EncounterCombatant,
    target: EncounterCombatant,
) -> bool:
    """Validate an explicitly configured other-creature turn-start Reaction."""
    rule = source.state.template.turn_start_save_reaction
    if rule is None or rule.trigger != "other_creature_turn_start":
        return False
    if source.combatant_id == target.combatant_id or source.side == target.side:
        return False
    if not source.state.is_alive or source.state.current_hp <= 0:
        return False
    if not target.state.is_alive or target.state.current_hp <= 0:
        return False
    if not is_available(source.state, "reaction"):
        return False
    if combatant_distance(source, target) > rule.range_ft:
        return False
    if rule.source_must_see_target and not can_see(source.state, target.state):
        return False
    if rule.target_must_see_source and not can_see(target.state, source.state):
        return False
    return True
