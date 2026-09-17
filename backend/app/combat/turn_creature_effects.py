from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup


def apply_turned_creature_effects(
    source: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    round_number: int,
    *,
    source_effect_id: str,
    turned_effect_id: str,
) -> list[str]:
    """Apply the shared 1-minute forced-retreat turn package used by holy turning features."""
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    common = dict(
        source_effect_id=source_effect_id,
        applied_round=round_number,
        expires_round=round_number + 10,
        expiry_timing="source_turn_start",
        affected_states=states,
        ends_on_damage=True,
        ends_if_source_incapacitated=True,
        ends_if_source_dead=True,
    )
    applied = [
        apply_timed_condition(
            target.state,
            turned_effect_id,
            source.combatant_id,
            turn_behavior="forced_retreat",
            **common,
        )
    ]
    for condition in ("frightened", "incapacitated"):
        if not condition_is_immune(target.state, condition):
            applied.append(apply_timed_condition(
                target.state,
                condition,
                source.combatant_id,
                **common,
            ))
    return [effect for effect in applied if effect is not None]
