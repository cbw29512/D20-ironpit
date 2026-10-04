from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.concentration import end_concentration, start_concentration
from app.combat.resources import spend_resource
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.spellcasting import legal_slot_levels, mark_slot_spell_cast
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.post_hit_save_condition import PostHitSaveConditionSpell
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import size_at_least

logger = logging.getLogger(__name__)


def _slot_level(caster: EncounterCombatant, action: PostHitSaveConditionSpell, turn_key: str) -> int | None:
    levels = legal_slot_levels(caster.state, turn_key, action.level, higher_slot_scaling=True)
    return min(levels) if levels else None


def resolve_post_hit_save_condition(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_key: str,
) -> BattleEvent | None:
    """Cast one post-hit Bonus Action save-condition spell after a weapon hit."""
    try:
        if not is_available(attacker.state, "bonus_action"):
            return None
        if target.state.current_hp <= 0 or target.state.is_dead:
            return None
        for action in attacker.state.template.post_hit_save_condition_spells:
            if attacker.state.concentration is not None:
                continue
            slot_level = _slot_level(attacker, action, turn_key)
            if slot_level is None:
                continue
            spend(attacker.state, action.action_cost)
            mark_slot_spell_cast(attacker.state, turn_key)
            spend_resource(attacker.state, f"spell-slot-{slot_level}", 1)
            affected = [member.state for member in [*setup.heroes, *setup.monsters]]
            start_concentration(
                attacker.state,
                attacker.combatant_id,
                action.id,
                round_number,
                affected,
                expires_round=round_number + action.duration_rounds,
                slot_level=slot_level,
            )
            advantage = ()
            if (
                action.size_save_advantage_from is not None
                and size_at_least(target.state.template.size, action.size_save_advantage_from)
            ):
                advantage = (f"{action.name} size",)
            roll, succeeded = resolve_saving_throw(
                target.state,
                action.save_ability,
                action.save_dc,
                dice,
                SavingThrowContext(
                    condition_id=action.failed_condition_id,
                    magical_effect=True,
                    spell_effect=True,
                    advantage_sources=advantage,
                ),
                round_number=round_number,
                encounter_roller=target,
                setup=setup,
            )
            applied: list[str] = []
            if succeeded and action.success_ends_spell:
                end_concentration(attacker.state, affected)
            elif not succeeded:
                applied_id = apply_timed_condition(
                    target.state,
                    action.failed_condition_id,
                    attacker.combatant_id,
                    source_effect_id=action.id,
                    source_template=attacker.state.template,
                    source_is_magical=True,
                    applied_round=round_number,
                    expires_round=round_number + action.duration_rounds,
                    expiry_timing="source_turn_end",
                    affected_states=affected,
                    use_default_poison_recovery=False,
                )
                if applied_id is not None:
                    applied.append(applied_id)
            description = (
                f"{attacker.state.template.name} casts {action.name}; "
                f"{target.state.template.name} {'succeeds' if succeeded else 'fails'} "
                f"the DC {action.save_dc} {action.save_ability.title()} save."
            )
            if applied:
                description += f" {target.state.template.name} is {applied[0].title()}."
            return BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=attacker.combatant_id,
                actor_name=attacker.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                saving_throw_roll=roll,
                save_ability=action.save_ability,
                save_dc=action.save_dc,
                save_succeeded=succeeded,
                applied_condition_ids=applied,
                feature_id=action.id,
                animation=action.animation,
                description=description,
            )
        return None
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Post-hit save-condition spell failed for %s.", attacker.combatant_id)
        raise RuntimeError("Post-hit save-condition spell could not be resolved.") from exc
