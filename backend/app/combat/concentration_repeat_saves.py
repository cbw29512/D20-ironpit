from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.action_economy import is_available, spend
from app.combat.defensive_modifier_rules import remove_owner_attack_ending_modifiers
from app.combat.spell_choice import SpellChoice
from app.combat.spell_fixed_slot_policy import choose_spell_action_at_slot
from app.combat.spell_save_effect_resolution import resolve_spell_save_effect
from app.domain.concentration_repeat_saves import ConcentrationRepeatSaveAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ConcentrationRepeatSaveChoice:
    action: ConcentrationRepeatSaveAction
    spell_choice: SpellChoice

    @property
    def expected_damage(self) -> float:
        return self.spell_choice.expected_damage


def _source_template(member: EncounterCombatant):
    state = member.state
    if state.replacement_form is not None:
        return state.replacement_form.original_template
    return state.template


def choose_concentration_repeat_save(
    member: EncounterCombatant,
    setup: EncounterSetup,
) -> ConcentrationRepeatSaveChoice | None:
    """Choose an Action granted by the spell the combatant is currently concentrating on."""
    try:
        state = member.state
        concentration = state.concentration
        if concentration is None or concentration.slot_level is None:
            return None
        source_template = _source_template(member)
        candidates: list[tuple[int, float, ConcentrationRepeatSaveChoice]] = []
        for action in source_template.concentration_repeat_save_actions:
            if action.source_spell_id != concentration.effect_id:
                continue
            if not is_available(state, action.action_cost):
                continue
            source_spell = next(
                (
                    spell
                    for spell in source_template.spell_save_actions
                    if spell.id == action.source_spell_id
                ),
                None,
            )
            if source_spell is None:
                raise ValueError(
                    f"{action.name} declares missing source spell {action.source_spell_id}."
                )
            if not source_spell.concentration:
                raise ValueError(
                    f"{action.name} source spell {source_spell.name} is not a Concentration spell."
                )
            spell_choice = choose_spell_action_at_slot(
                member,
                setup,
                source_spell,
                concentration.slot_level,
            )
            if spell_choice is None:
                continue
            choice = ConcentrationRepeatSaveChoice(action, spell_choice)
            candidates.append((action.priority, choice.expected_damage, choice))
        return max(candidates, key=lambda item: item[:2])[2] if candidates else None
    except Exception:
        logger.exception(
            "Failed to choose concentration repeat-save Action for %s.",
            member.combatant_id,
        )
        raise


def resolve_concentration_repeat_save(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    choice: ConcentrationRepeatSaveChoice,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve an ongoing concentration spell Action without casting or spending another slot."""
    try:
        state = member.state
        concentration = state.concentration
        action = choice.action
        if (
            concentration is None
            or concentration.effect_id != action.source_spell_id
            or concentration.slot_level != choice.spell_choice.slot_level
        ):
            raise ValueError(f"{action.name} no longer has its required active Concentration.")
        if not is_available(state, action.action_cost):
            raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")

        spend(state, action.action_cost)
        remove_owner_attack_ending_modifiers(state)
        actor_name = _source_template(member).name
        events = [BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=member.combatant_id,
            actor_name=actor_name,
            feature_id=action.id,
            animation=action.animation,
            description=(
                f"{actor_name} uses {action.name} from the ongoing "
                f"{choice.spell_choice.action.name} spell."
            ),
        )]
        sequence += 1
        effect_events, sequence = resolve_spell_save_effect(
            sequence,
            round_number,
            member,
            setup,
            choice.spell_choice,
            turn_key,
            dice,
        )
        events.extend(effect_events)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Concentration repeat-save Action failed for %s.",
            member.combatant_id,
        )
        raise RuntimeError("Concentration repeat-save Action could not be resolved.") from exc
