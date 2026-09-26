from __future__ import annotations

import logging

from app.combat.action_economy import is_available
from app.combat.replacement_forms import resolve_replacement_form_action
from app.combat.resources import resource_available
from app.combat.spell_policy import choose_named_spell
from app.combat.spell_resolution import resolve_spell
from app.content.replacement_form_compiler import compile_replacement_form_template
from app.content.replacement_form_registry import replacement_form_source_template
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


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
        if state.replacement_form is not None or not is_available(state, "action"):
            return [], sequence
        actions = state.template.replacement_form_actions
        if not actions:
            return [], sequence
        action = actions[0]
        if not resource_available(state, action.resource_id, action.resource_cost):
            return [], sequence

        if action.setup_spell_id:
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
                    return resolve_spell(
                        sequence,
                        round_number,
                        member,
                        setup,
                        choice,
                        turn_key,
                        dice,
                    )
                return [], sequence

        source = replacement_form_source_template(
            state.template.ruleset,
            action.form_template_id,
        )
        active = compile_replacement_form_template(
            state.template,
            source,
            retain_spellcasting=action.retain_spellcasting,
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
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Replacement-form setup failed for %s.", member.combatant_id)
        raise RuntimeError("Replacement-form setup could not be resolved.") from exc
