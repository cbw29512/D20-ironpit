from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.replacement_form_offense import defer_emergency_form_for_spell
from app.combat.replacement_forms import resolve_replacement_form_action
from app.combat.resource_conversion import restoration_conversion, resolve_resource_conversion
from app.combat.resources import resource_available
from app.combat.spell_fixed_slot_policy import choose_named_spell
from app.combat.spell_resolution import resolve_spell
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.content.replacement_form_registry import replacement_form_source_template
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def ai_may_start_replacement_form(state, action, owner_template) -> bool:
    """AI selection gate, not a restriction on the printed source feature."""
    try:
        if action.ai_use_policy != "emergency_only":
            return True
        if state.replacement_form is not None:
            return False
        if (action.hp_mode == "retain_owner"
            and action.temporary_hp_on_enter <= state.temporary_hp):
            return False  # No gain: preserve limited form uses.
        return 0 < state.current_hp <= owner_template.max_hp * action.ai_emergency_hp_fraction
    except Exception as exc:
        logger.exception(
            "Cannot evaluate replacement-form AI eligibility for action %s.",
            getattr(action, "id", "<unknown>"),
        )
        raise RuntimeError("Replacement-form AI eligibility could not be evaluated.") from exc


def resolve_replacement_form_setup(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Cast a declared setup spell, then transform on a later legal Action."""
    try:
        state = member.state
        owner_template = (
            state.replacement_form.original_template
            if state.replacement_form is not None else state.template
        )
        actions = owner_template.replacement_form_actions
        if not actions:
            return [], sequence
        action = actions[0]
        if not ai_may_start_replacement_form(state, action, owner_template):
            return [], sequence
        if state.replacement_form is not None and not action.replace_existing_form:
            return [], sequence
        if defer_emergency_form_for_spell(member, setup, action, turn_key):
            return [], sequence
        if not is_available(state, action.action_cost):
            return [], sequence
        events: list[BattleEvent] = []
        if not resource_available(state, action.resource_id, action.resource_cost):
            conversion = restoration_conversion(state, action.resource_id, turn_key)
            if conversion is None:
                return [], sequence
            events.append(resolve_resource_conversion(
                state,
                conversion,
                sequence=sequence,
                round_number=round_number,
                actor_id=member.combatant_id,
                turn_key=turn_key,
            ))
            sequence += 1

        # Emergency forms bypass optional setup spells; they must work even
        # when no slot remains or an immediate defensive Action is needed.
        if action.setup_spell_id and action.ai_use_policy != "emergency_only":
            concentration = state.concentration
            setup_active = concentration is not None and concentration.effect_id == action.setup_spell_id
            if not setup_active:
                choice = choose_named_spell(
                    member,
                    setup,
                    turn_key,
                    action.setup_spell_id,
                )
                if choice is not None:
                    spell_events, sequence = resolve_spell(
                        sequence,
                        round_number,
                        member,
                        setup,
                        choice,
                        turn_key,
                        dice,
                    )
                    return [*events, *spell_events], sequence
                return [], sequence

        source = replacement_form_source_template(
            owner_template.ruleset,
            action.form_template_id,
        )
        active = compile_replacement_form_template(
            owner_template,
            source,
            retain_spellcasting=action.retain_spellcasting,
            retained_spell_action_ids=action.retained_spell_action_ids,
            retain_creature_type=action.retain_creature_type,
            retain_hit_points=action.hp_mode == "retain_owner",
        )
        result = resolve_replacement_form_action(state, action, active)
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=state.template.name,
            feature_id=action.id,
            resource_remaining=result.resource_remaining,
            animation="transform",
            description=(
                f"{result.form_name} uses {action.name} and enters the "
                f"{source.name} replacement form."
            ),
        )
        return [*events, event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Replacement-form setup failed for %s.", member.combatant_id)
        raise RuntimeError("Replacement-form setup could not be resolved.") from exc
