"""Source-gated conditional immunity for 2014 Steadfast; no persistent immunity flag."""
from __future__ import annotations

from app.combat.ally_context import has_visible_active_ally_within
from app.domain.encounters import EncounterCombatant, EncounterSetup


def steadfast_frightened_immunity(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    condition_id: str,
) -> bool:
    """Steadfast applies only while a live visible ally remains within 30 feet."""
    if condition_id != "frightened":
        return False
    if actor.state.template.ruleset != "2014":
        return False
    if "Steadfast" not in actor.state.template.source_trait_names:
        return False
    return has_visible_active_ally_within(actor, setup, 30)
