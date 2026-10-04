from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.content.monster_creature_types import base_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def _aura_active(source: EncounterCombatant, action_id: str) -> bool:
    state = source.state
    if state.is_dead or not state.is_alive or state.current_hp <= 0 or is_incapacitated(state):
        return False
    return any(
        effect.source_id == source.combatant_id and effect.source_effect_id == action_id
        for effect in state.timed_effects
    )


def apply_melee_hit_save_retaliation(
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    *,
    melee: bool,
    dice,
    setup: EncounterSetup | None,
    round_number: int,
    affected_states=None,
) -> str | None:
    """Resolve aura-scoped melee-hit save riders after a qualifying melee hit."""
    try:
        if not melee or setup is None or attacker.state.is_dead or not attacker.state.is_alive:
            return None
        attacker_type = base_creature_type(attacker.state.template.creature_type)
        if attacker_type is None:
            return None
        allies = setup.heroes if defender.side == "heroes" else setup.monsters
        if defender.state.is_dead or not defender.state.is_alive:
            return None
        for source in allies:
            for action in source.state.template.timed_self_buff_actions:
                aura = action.friendly_save_advantage_aura
                if aura is None or aura.melee_hit_save_retaliation is None:
                    continue
                if not _aura_active(source, action.id):
                    continue
                if combatant_distance(source, defender) > aura.radius_ft:
                    continue
                rider = aura.melee_hit_save_retaliation
                if attacker_type not in rider.attacker_creature_types:
                    continue
                _, succeeded = resolve_saving_throw(
                    attacker.state,
                    rider.save_ability,
                    rider.save_dc,
                    dice,
                    SavingThrowContext(
                        condition_id=rider.condition_id,
                        magical_effect=rider.magical_effect,
                    ),
                    round_number=round_number,
                    encounter_roller=attacker,
                    setup=setup,
                )
                if succeeded:
                    return None
                return apply_timed_condition(
                    attacker.state,
                    rider.condition_id,
                    source.combatant_id,
                    source_effect_id=action.id if rider.bind_to_source_effect else f"{action.id}-melee-blind",
                    source_template=source.state.template,
                    source_is_magical=rider.magical_effect,
                    applied_round=round_number,
                    expires_round=None if rider.bind_to_source_effect else round_number + rider.duration_rounds,
                    expiry_timing=None if rider.bind_to_source_effect else rider.expiry_timing,
                    affected_states=affected_states,
                    use_default_poison_recovery=False,
                )
        return None
    except Exception:
        logger.exception(
            "Failed melee-hit save retaliation for attacker %s vs %s.",
            attacker.combatant_id,
            defender.combatant_id,
        )
        raise
