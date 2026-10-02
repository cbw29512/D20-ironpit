from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.deferred_save_effect_outcomes import resolve_deferred_effect_outcome
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def deferred_save_effect_candidate(
    actor: EncounterCombatant,
    setup: EncounterSetup,
    *,
    require_action: bool = True,
) -> EncounterCombatant | None:
    """Return the first living marked target when the requested activation path is legal."""
    try:
        rule = actor.state.template.progression_features.deferred_save_effect
        if rule is None or (require_action and not is_available(actor.state, "action")):
            return None
        by_id = {
            member.combatant_id: member
            for member in [*setup.heroes, *setup.monsters]
        }
        for mark in actor.state.deferred_effects:
            if mark.source_id != rule.source_id:
                continue
            target = by_id.get(mark.target_id)
            if (
                target is not None
                and target.state.is_alive
                and not target.state.is_dead
                and target.state.current_hp > 0
            ):
                return target
        return None
    except Exception as exc:
        logger.exception("Failed to select deferred save effect target for %s.", actor.combatant_id)
        raise RuntimeError("Deferred save effect target could not be selected.") from exc


def resolve_deferred_save_effect(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    *,
    spend_action: bool = True,
) -> BattleEvent | None:
    """Resolve an armed effect through shared save, typed damage, and zero-HP lifecycles."""
    try:
        target = deferred_save_effect_candidate(actor, setup, require_action=spend_action)
        if target is None:
            return None
        rule = actor.state.template.progression_features.deferred_save_effect
        if rule is None:
            raise ValueError("Deferred effect candidate exists without immutable source data.")

        hp_before = target.state.current_hp
        temp_before = target.state.temporary_hp
        death_success_before = target.state.death_save_successes
        death_failure_before = target.state.death_save_failures
        roll, succeeded = resolve_saving_throw(target.state, rule.save_ability, rule.save_dc, dice)
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        damage_roll, components = resolve_deferred_effect_outcome(
            target.state,
            rule,
            succeeded,
            dice,
            affected,
        )

        if spend_action:
            spend(actor.state, "action")
        actor.state.deferred_effects = [
            item for item in actor.state.deferred_effects
            if not (item.source_id == rule.source_id and item.target_id == target.combatant_id)
        ]
        description = (
            f"{actor.state.template.name} activates {rule.source_name} on "
            f"{target.state.template.name}; the {rule.save_ability.title()} save "
            f"{'succeeds' if succeeded else 'fails'}."
        )
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=actor.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=roll,
            save_ability=rule.save_ability,
            save_dc=rule.save_dc,
            save_succeeded=succeeded,
            damage_roll=damage_roll,
            damage_components=components,
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            temporary_hp_before=temp_before,
            temporary_hp_after=target.state.temporary_hp,
            death_save_successes_before=death_success_before,
            death_save_failures_before=death_failure_before,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable,
            is_dead=target.state.is_dead,
            feature_id=rule.source_id,
            animation="save-effect",
            description=description,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve deferred save effect for %s.", actor.combatant_id)
        raise RuntimeError("Deferred save effect could not be resolved.") from exc
