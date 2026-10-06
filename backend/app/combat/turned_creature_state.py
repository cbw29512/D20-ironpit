from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def apply_turned_creature_effects(
    source: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    round_number: int,
    *,
    source_effect_id: str,
    turned_effect_id: str,
    include_frightened: bool = True,
    include_incapacitated: bool = True,
    suppress_action: bool = False,
    suppress_bonus_action: bool = False,
    suppress_reactions: bool = False,
    suppress_movement: bool = False,
    turn_behavior: str = "forced_retreat",
    repeat_save_ability: str | None = None,
    repeat_save_dc: int | None = None,
    repeat_save_timing: str | None = None,
    expires_rounds: int | None = 10,
    expiry_timing: str | None = "source_turn_start",
    ends_if_source_incapacitated: bool = True,
    ends_if_source_dead: bool = True,
) -> list[str]:
    """Apply the shared turn package through the ordinary condition lifecycle."""
    try:
        states = [member.state for member in [*setup.heroes, *setup.monsters]]
        common = dict(
            source_effect_id=source_effect_id,
            source_template=source.state.template,
            source_is_magical=True,
            applied_round=round_number,
            expires_round=(round_number + expires_rounds) if expires_rounds is not None else None,
            expiry_timing=expiry_timing,
            affected_states=states,
            ends_on_damage=True,
            ends_if_source_incapacitated=ends_if_source_incapacitated,
            ends_if_source_dead=ends_if_source_dead,
        )
        applied = [
            apply_timed_condition(
                target.state,
                turned_effect_id,
                source.combatant_id,
                turn_behavior=turn_behavior,
                suppress_action=suppress_action,
                suppress_bonus_action=suppress_bonus_action,
                suppress_reactions=suppress_reactions,
                suppress_movement=suppress_movement,
                repeat_save_ability=repeat_save_ability,
                repeat_save_dc=repeat_save_dc,
                repeat_save_timing=repeat_save_timing,
                repeat_save_context=SavingThrowContext(
                    magical_effect=True, source_creature_type=source.state.template.creature_type,
                    condition_id="frightened" if include_frightened else None,
                    effect_tags=frozenset({"turning", *(["frightened"] if include_frightened else [])}),
                ) if repeat_save_timing else None,
                **common,
            )
        ]
        conditions = []
        if include_frightened:
            conditions.append("frightened")
        if include_incapacitated:
            conditions.append("incapacitated")
        for condition in conditions:
            if not condition_is_immune(target.state, condition):
                applied.append(apply_timed_condition(
                    target.state,
                    condition,
                    source.combatant_id,
                    **common,
                ))
        return [effect for effect in applied if effect is not None]
    except Exception:
        logger.exception("Failed turning state application from %s to %s.", source.combatant_id, target.combatant_id)
        raise
